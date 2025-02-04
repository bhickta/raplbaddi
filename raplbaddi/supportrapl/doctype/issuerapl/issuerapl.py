# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from .maps import GoogleMapClient
from frappe.model.document import Document

mapclient = GoogleMapClient()


class IssueRapl(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.contacts.doctype.contact_phone.contact_phone import ContactPhone
        from frappe.types import DF
        from raplbaddi.raplbaddi.doctype.issuerapl_item.issuerapl_item import IssueRaplItem
        from raplbaddi.supportrapl.doctype.spare_parts_entry.spare_parts_entry import SparePartsEntry

        address_description: DF.LongText | None
        aerial_kilometer: DF.Int
        amended_from: DF.Link | None
        amount: DF.Currency
        brand_name: DF.Link | None
        complaint_source_group: DF.Data | None
        cooler_model: DF.Link | None
        custom_creation_date: DF.Date | None
        customer_address: DF.Text | None
        customer_address_state: DF.Data | None
        customer_confirmation: DF.Literal["Not Taken", "Positive", "Negative"]
        customer_contact: DF.Table[ContactPhone]
        customer_name: DF.Data
        customer_phone_number: DF.Data | None
        expected_visit_date: DF.Date | None
        extra_cost: DF.Float
        geyser_capacity: DF.Link | None
        invoice_date: DF.Date | None
        is_custom_amount: DF.Check
        issuerapl_items: DF.Table[IssueRaplItem]
        kilometer: DF.Float
        latitude: DF.Data | None
        longitude: DF.Data | None
        model: DF.Link | None
        naming_series: DF.Literal["RAPL-"]
        no_of_pcs: DF.Float
        no_of_visits: DF.Int
        payment_done: DF.Literal["Unpaid", "Paid"]
        pincode_service_centre: DF.Int
        product: DF.Literal["Geyser", "Desert Air Cooler"]
        product_photo: DF.AttachImage | None
        remarks: DF.SmallText | None
        service_centre: DF.Link
        service_centre_phone_number: DF.Data | None
        service_delivered: DF.Literal["No", "Yes"]
        spare_parts_entry: DF.Table[SparePartsEntry]
        status: DF.Literal["Open", "Closed", "Cancelled"]
        system_amount: DF.Float
    # end: auto-generated types
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.post_init()

    def post_init(self):
        pass
    
    def before_insert(self):
        if not self.custom_creation_date:
            self.custom_creation_date = frappe.utils.today()

    def validate(self):
        self.validate_service_centre()
        self.set_kilometers()
        self.set_amount()
        self.validate_is_payable()

    def validate_service_centre(self):
        if not self.service_centre:
            frappe.throw("Please Select a Service Centre")

    def validate_is_payable(self):
        if self.is_payable and not self.amount:
            frappe.throw("Please Enter the Amount as service is Payable")

    def set_kilometers(self):
        fields = ["latitude", "longitude", "service_centre"]
        changed_fields = False
        for field in fields:
            if self.is_new():
                break
            if str(self._doc_before_save.get(field)) != str(self.get(field)):
                changed_fields = True
                break
        if not self.kilometer or self._action == "submit" or changed_fields:
            self._set_kilometers()

    def _set_kilometers(self):
        org_lat, org_lng = self.latitude, self.longitude
        sc_lat, sc_lng = frappe.get_cached_value(
            "Service Centre", self.service_centre, ["latitude", "longitude"]
        )
        new_kilometer = mapclient.road_distance(
            origin=(org_lat, org_lng), destination=(sc_lat, sc_lng)
        )
        if new_kilometer != self.kilometer:
            self.kilometer = new_kilometer
            frappe.msgprint(
                f"Kilometer has been updated to {self.kilometer} kilometers",
                title="Updated Kilometer",
            )

    def set_amount(self):
        self._set_amount()
    
    def _set_amount(self):
        self._set_rates()
        kilometer_category = float(self.rates.get("kilometer_category", 0))
        net_kilometer = max(0, float(self.kilometer) - kilometer_category)

        extra_pcs_rate = (
            self.rates["per_kilometer_rate_for_2"]
            if self.no_of_pcs == 2
            else (
                self.rates["per_kilometer_rate_for_3_or_more"]
                if self.no_of_pcs > 2
                else 0
            )
        )

        fixed_rate = float(self.rates.get("fixed_rate", 0))
        per_kilometer_rate = float(self.rates.get("per_kilometer_rate", 0))
        extra_cost = self.extra_cost or 0
        no_of_visits = self.no_of_visits or 1

        final_rate = (
            fixed_rate
            + (extra_pcs_rate * (self.no_of_pcs - 1))
            + (per_kilometer_rate * net_kilometer)
            + extra_cost
        ) * no_of_visits
        self.system_amount = final_rate
        if not self.is_custom_amount:
            self.amount = self.system_amount
        self.extra_cost = self.system_amount - self.amount
    
    def _set_rates(self, service_centre=None):
        service_centre_name = service_centre or self.service_centre
        doc = frappe.get_doc("Service Centre", service_centre_name)
        self.rates = {
            "kilometer_category": doc.kilometer_category,
            "fixed_rate": doc.fixed_rate,
            "per_kilometer_rate": doc.per_kilometer_rate,
            "per_kilometer_rate_for_2": doc.per_kilometer_rate_for_2,
            "per_kilometer_rate_for_3_or_more": doc.per_kilometer_rate_for_3_or_more,
            "is_payable": doc.is_payable,
        }

    def is_payable(self):
        is_payable = False
        is_payable = self.rates.get("is_payable")
        fields = [
            "fixed_rate",
            "per_kilometer_rate",
            "per_kilometer_rate_for_2",
            "per_kilometer_rate_for_3_or_more",
        ]
        for field in fields:
            if self.rates.get(field):
                is_payable = True
                break
        return is_payable

    @frappe.whitelist()
    def get_addresses(self):
        self.service_centres = frappe.get_all(
            "Service Centre",
            filters={"is_disabled": 0},
            fields=["latitude", "longitude", "name"],
        )
        self._nearest_sc()
        ret = []
        for sc in self.areal_distances:
            key = list(sc.keys())[0]
            distance = list(sc.values())[0]["distance"]
            formatted_output = f"{key}: {distance}"
            ret.append(formatted_output)
        return ret

    def _nearest_sc(self, top: int = 3):
        self.areal_distances = []
        for sc in self.service_centres:
            distance = mapclient._get_lat_lng_distance(
                (self.latitude, self.longitude), (sc["latitude"], sc["longitude"])
            )
            self.areal_distances.append(
                {
                    sc["name"]: {
                        "distance": int(distance),
                        "coordinates": {
                            "latitude": sc["latitude"],
                            "longitude": sc["longitude"],
                        },
                    }
                }
            )

        self.areal_distances.sort(key=lambda x: list(x.values())[0]["distance"])

    def before_submit(self):
        self.validate_mandatory()
    
    def validate_mandatory(self):
        for item in self.issuerapl_items:
            if not item.sub_issue or item.issue_type:
                frappe.throw(f"Please select issue type and sub issue in row {item.idx}")
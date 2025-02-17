# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ServiceCentre(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        account_holder_name: DF.Data
        address: DF.Data
        bank_account_no: DF.Data
        bank_name: DF.Data
        country: DF.Link | None
        create_warehouse_customer: DF.Check
        customer: DF.Link | None
        defective_warehouse: DF.Link | None
        district: DF.Link | None
        fixed_rate: DF.Float
        ifsc_code: DF.Data
        is_disabled: DF.Check
        is_payable: DF.Check
        kilometer_category: DF.Float
        latitude: DF.Data | None
        longitude: DF.Data | None
        main_warehouse: DF.Link | None
        per_kilometer_rate: DF.Float
        per_kilometer_rate_for_2: DF.Float
        per_kilometer_rate_for_3_or_more: DF.Float
        phone_no: DF.Data
        pincode: DF.Data
        service_centre_name: DF.Data
        state: DF.Link | None
        supplier: DF.Link | None
        upi_id: DF.Data
        user: DF.Link
    # end: auto-generated types

    def after_rename(self, name, merge=False, force=False, validate_rename=True):
        frappe.rename_doc("Warehouse", self.main_warehouse, self.name + "-WH-Main", True)
        frappe.rename_doc("Warehouse", self.defective_warehouse, self.name + "-WH-Defective", True)

    def before_insert(self):
        self.check_warehouse_customer_supplier()

    def check_warehouse_customer_supplier(self):
        if not self.create_warehouse_customer and (
            not self.customer or not self.supplier or not self.main_warehouse or not self.defective_warehouse
        ):
            frappe.throw(
                "Please enter warehouse(main, defective) and customer supplier or check create warehouse and customer supplier"
            )
        if self.create_warehouse_customer:
            self._create_warehouse_customer_supplier()

    def _create_warehouse_customer_supplier(self):
        if not self.service_centre_name:
            frappe.throw("Please enter Service Centre Name")

        self.main_warehouse = _get_or_create_doc(
            "Warehouse",
            self.service_centre_name,
            {
                "parent_warehouse": "Service Centre - RAPL",
                "warehouse_name": self.service_centre_name,
            },
        )

        self.defective_warehouse = _get_or_create_doc(
            "Warehouse",
            self.service_centre_name + " Defective",
            {
                "parent_warehouse": "Service Centre - RAPL",
                "warehouse_name": self.service_centre_name + " Defective",
            },
        )

        self.settings = frappe.get_single("Raplbaddi Settings")
        if not self.settings.service_centre_customer_group or not self.settings.service_centre_supplier_group:
            frappe.throw(
                "Please enter service centre customer group and supplier group in Raplbaddi Settings"
            )
        
        self.customer = _get_or_create_doc(
            "Customer",
            self.service_centre_name,
            {
                "customer_name": self.service_centre_name,
                "customer_group": self.settings.service_centre_customer_group,
            },
        )

        self.supplier = _get_or_create_doc(
            "Supplier",
            self.service_centre_name,
            {
                "supplier_name": self.service_centre_name,
                "supplier_group": self.settings.service_centre_supplier_group,
            },
        )

    def validate(self):
        self.check_warehouse_customer_supplier()
        self.validate_mandatory()
        self.create_warehouse_customer = 0

    def validate_mandatory(self):
        mandatory_fields = ["main_warehouse", "defective_warehouse", "customer"]
        for field in mandatory_fields:
            if not self.get(field):
                frappe.throw(f"Please enter {field}")


def _get_or_create_doc(doctype, name, defaults):
    try:
        new_doc = frappe.new_doc(doctype)
        new_doc.update(defaults)
        new_doc.save()
    except frappe.DuplicateEntryError as e:
        new_doc = frappe.get_doc(doctype, e.args[1])
    return new_doc.name
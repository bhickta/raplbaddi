# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from .maps import GoogleMapClient
from frappe.model.document import Document

mapclient = GoogleMapClient()


class IssueRapl(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_sc()

    def get_sc(self):
        self.service_centres = frappe.get_all(
            "Service Centre",
            filters={"is_disabled": 0},
            fields=["latitude", "longitude", "name"],
        )


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

    @frappe.whitelist()
    def get_addresses(self):
        self._nearest_sc()
        ret = []
        for sc in self.areal_distances:
            key = list(sc.keys())[0]
            distance = list(sc.values())[0]["distance"]
            formatted_output = f"{key}: {distance}"
            ret.append(formatted_output)
        return ret

    @frappe.whitelist()
    def set_kilometers(self, service_centre=None, service_centres=None):
        self.curr_service_centre = service_centre or self.service_centre
        if service_centres:
            self.service_centres = service_centres
        print(self.service_centres)
        lat, lng = None, None
        for sc in self.service_centres:
            if sc["name"] == self.curr_service_centre:
                lat = sc["latitude"]
                lng = sc["longitude"]
                break
        if lat is not None and lng is not None:
            distance = mapclient.road_distance(
                origin=(lat, lng), destination=(self.latitude, self.longitude)
            )
            distance = 10
            self.kilometer = distance * 2
            self._get_rates(self.curr_service_centre)
        return

    def _get_rates(self, service_centre=None):
        rates = frappe.get_all(
            "Service Centre",
            [
                "kilometer_category",
                "fixed_rate",
                "per_kilometer_rate",
                "per_kilometer_rate_for_2",
                "per_kilometer_rate_for_3_or_more",
                "is_payable"
            ],
            filters={
                "name": self.service_centre if not service_centre else service_centre
            },
        )[0]
        (
            kilometer_category,
            fixed_rate,
            per_kilometer_rate,
            per_kilometer_rate_for_2,
            per_kilometer_rate_for_3_or_more,
            is_payable
        ) = (
            rates.get("kilometer_category"),
            rates.get("fixed_rate"),
            rates.get("per_kilometer_rate"),
            rates.get("per_kilometer_rate_for_2"),
            rates.get("per_kilometer_rate_for_3_or_more"),
            rates.get("is_payable"),
        )
        net_kilometer = max(0, float(self.kilometer) - float(kilometer_category))
        extra_pcs_rate = 0
        if self.no_of_pcs == 2:
            extra_pcs_rate = per_kilometer_rate_for_2
        elif self.no_of_pcs > 2:
            extra_pcs_rate = per_kilometer_rate_for_3_or_more
        final_rate = (
            float(fixed_rate)
            + (extra_pcs_rate * (self.no_of_pcs - 1))
            + (float(per_kilometer_rate) * float(net_kilometer))
            + self.extra_cost
        )
        final_rate = self.no_of_visits * final_rate
        if is_payable:
            self.amount = final_rate
        else:
            self.amount = 0

def set_kilometers(doc: IssueRapl):
    service_centres = frappe.get_all(
        "Service Centre",
        filters={"is_disabled": 0},
        fields=["latitude", "longitude", "name"],
    )
    doc.set_kilometers(service_centres=service_centres)
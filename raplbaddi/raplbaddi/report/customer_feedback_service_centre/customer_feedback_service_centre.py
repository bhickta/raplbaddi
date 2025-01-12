# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.core.doctype.user_permission.user_permission import get_user_permissions
from raplbaddi.raplbaddi.report.utils.service_centre import ServiceCentreReport
  
class IssueComplaintsReport(ServiceCentreReport):
    def __init__(self, filters=None):
        super().__init__(filters)

    def fetch_data(self):
        query = """
            SELECT
                ir.name AS complaint_no,
                ir.customer_name AS customer_name,
                GROUP_CONCAT(cp.phone) AS contact_numbers,
                ir.customer_confirmation AS feedback,
                ir.service_delivered AS service_delivered,
                ir.status AS status,
                ir.remarks AS customer_remarks,
                1 AS row_no
            FROM
                `tabIssueRapl` ir
            JOIN
                `tabContact Phone` cp ON ir.name = cp.parent
            WHERE
                ir.service_delivered = %(service_delivered)s
                AND ir.customer_confirmation IN %(customer_confirmation)s
                AND ir.status != 'Cancelled'
        """
        params = {
            "service_delivered": self.filters.get("service_delivered", "Yes"),
            "customer_confirmation": tuple(
                self.filters.get("customer_confirmation", ["Not Taken", "Negative"])
            ),
        }

        if self.allowed_service_centres:
            query += " AND ir.service_centre IN %(service_centre)s"
            params["service_centre"] = tuple(self.allowed_service_centres)

        query += """
            GROUP BY
                ir.name, ir.customer_name, ir.customer_confirmation, 
                ir.service_delivered, ir.status, ir.remarks
        """

        return frappe.db.sql(query, params, as_dict=True)

    def fetch_columns(self):
        """Define the report columns."""
        return [
            {
                "label": "Complaint No",
                "fieldname": "complaint_no",
                "fieldtype": "Link",
                "options": "IssueRapl",
                "width": 120,
            },
            {
                "label": "Customer Name",
                "fieldname": "customer_name",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": "Contact Numbers",
                "fieldname": "contact_numbers",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "label": "Feedback",
                "fieldname": "feedback",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "label": "Service Delivered",
                "fieldname": "service_delivered",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "label": "Status",
                "fieldname": "status",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "label": "Customer Remarks",
                "fieldname": "customer_remarks",
                "fieldtype": "Small Text",
                "width": 200,
            },
            {"label": "Row No", "fieldname": "row_no", "fieldtype": "Int", "width": 50},
        ]


def execute(filters=None):
    report = IssueComplaintsReport(filters)
    return report.run()

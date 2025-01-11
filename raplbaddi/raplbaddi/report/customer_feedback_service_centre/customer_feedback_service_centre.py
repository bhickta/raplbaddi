# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.core.doctype.user_permission.user_permission import get_user_permissions


class IssueComplaintsReport:
    """Generate the Issue Complaints Report."""

    def __init__(self, filters=None):
        self.filters = filters or {}
        self.allowed_groups = []

    def get_allowed_service_centres(self):
        user_permissions = get_user_permissions(frappe.session.user)
        allowed_service_centres = [groups['doc'] for groups in user_permissions.get('Service Centre', [])]
        return allowed_service_centres

    def validate_permissions(self):
        self.allowed_service_centres = self.get_allowed_service_centres()

    def run(self):
        """Fetch and process data for the report."""
        self.validate_permissions()
        data = self.fetch_data()
        columns = self.get_columns()
        return columns, data

    def fetch_data(self):
        """Fetch the report data based on filters."""
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

        # Apply customer group filtering only if allowed_groups has elements
        if self.allowed_service_centres:
            query += " AND ir.service_centre IN %(service_centre)s"
            params["service_centre"] = tuple(self.allowed_service_centres)

        query += """
            GROUP BY
                ir.name, ir.customer_name, ir.customer_confirmation, 
                ir.service_delivered, ir.status, ir.remarks
        """

        return frappe.db.sql(query, params, as_dict=True)

    def get_columns(self):
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
    """Entry point for the report."""
    report = IssueComplaintsReport(filters)
    return report.run()

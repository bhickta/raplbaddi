# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt


import frappe
from raplbaddi.raplbaddi.report.utils.service_centre import ServiceCentreReport

class PendingComplaintReport(ServiceCentreReport):
    def __init__(self, filters=None):
        super().__init__(filters)

    def fetch_data(self):
        query = """
            SELECT
                i.creation as date,
                i.name AS ticket_number,
                i.service_centre AS service_centre,
                i.customer_name AS customer_name,
                i.customer_address AS address,
                i.product AS product,
                i.brand_name AS brand,
                i.issue_type AS issue,
                i.service_delivered AS status,
                GROUP_CONCAT(j.phone SEPARATOR ', ') AS contact,
                1 as No
            FROM 
                `tabIssueRapl` AS i
            JOIN 
                `tabContact Phone` AS j ON j.parent = i.name
            where 
                i.service_delivered = 'No' and i.status = 'Open'
        """

        params = {}

        if self.allowed_service_centres:
            query += " AND i.service_centre IN %(service_centre)s"
            params["service_centre"] = tuple(self.allowed_service_centres)

        query += """
            GROUP BY 
                i.name
        """
        print(query)
        return frappe.db.sql(query, params, as_dict=True)

    def get_columns(self):
        """Define the report columns."""
        return [
            {
                "label": "Date",
                "fieldname": "date",
                "fieldtype": "Date",
                "width": 120,
            },
            {
                "label": "Ticket Name",
                "fieldname": "ticket_number",
                "fieldtype": "Link",
                "options": "IssueRapl",
                "width": 150,
            },
            {
                "label": "Service Centre",
                "fieldname": "service_centre",
                "fieldtype": "Link",
                "options": "Service Centre",
                "width": 200,
            },
            {
                "label": "Customer Name",
                "fieldname": "customer_name",
                "fieldtype": "Data",
                "width": 180,
            },
            {
                "label": "Address",
                "fieldname": "address",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "label": "Product",
                "fieldname": "product",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "label": "Brand",
                "fieldname": "brand",
                "fieldtype": "Data",
                "width": 100,
            },
            {
                "label": "Issue",
                "fieldname": "issue",
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
                "label": "Contact",
                "fieldname": "contact",
                "fieldtype": "Data",
                "width": 100,
            },
        ]


def execute(filters=None):
    report = PendingComplaintReport(filters)
    return report.run()
# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from raplbaddi.raplbaddi.report.utils.service_centre import ServiceCentreReport


class CustomerFeedbackReport(ServiceCentreReport):
    def __init__(self, filters=None):
        super().__init__(filters)

    def fetch_data(self):
        query = """
            SELECT
                ir.name AS 'complaint_no',
                CONCAT(
                    UPPER(SUBSTRING(ir.customer_name, 1, 1)),
                    LOWER(SUBSTRING(ir.customer_name, 2))
                ) AS 'customer_name',
                IFNULL(GROUP_CONCAT(DISTINCT cp.phone), '') AS 'contact',
                ir.customer_confirmation AS 'feedback',
                ir.service_delivered AS 'service_delivered',
                ir.status AS 'status',
                ir.expected_visit_date,
                ir.remarks AS 'customer_remarks',
                1 AS 'no'
            FROM
                `tabIssueRapl` AS ir
            LEFT JOIN
                `tabContact Phone` AS cp ON ir.name = cp.parent
            WHERE
                ir.service_delivered = 'Yes'
                AND ir.customer_confirmation IN ('Not Taken', 'Negative')
                AND ir.status != 'Cancelled'
            GROUP BY
                ir.name, ir.customer_name, ir.customer_confirmation, ir.service_delivered, ir.remarks
            ORDER BY 
                ir.name DESC
        """
        raw_data = frappe.db.sql(query, as_dict=True)
        return raw_data

    def fetch_columns(self):
        return [
            {
                "label": "Complaint No.",
                "fieldname": "complaint_no",
                "fieldtype": "Link",
                "options": "IssueRapl",
                "width": 120,
            },
            {
                "label": "Customer Name",
                "fieldname": "customer_name",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "label": "Contact",
                "fieldname": "contact",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "label": "Feedback",
                "fieldname": "feedback",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "label": "Service Delivered",
                "fieldname": "service_delivered",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": "Status",
                "fieldname": "status",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": "Close Date",
                "fieldname": "expected_visit_date",
                "fieldtype": "Date",
                "width": 100,
            },
            {
                "label": "No",
                "fieldname": "no",
                "fieldtype": "Int",
                "width": 50,
            },
            {
                "label": "Customer Remarks",
                "fieldname": "customer_remarks",
                "fieldtype": "Data",
                "width": 300,
            },
        ]

    def get_message(self):
        return """
            <h1 style='text-align:center; color:orange;'>Report for Complaints with Feedback 'Not Taken' or 'Negative'</h1>
        """
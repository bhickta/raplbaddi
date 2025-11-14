# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from raplbaddi.raplbaddi.report.utils.service_centre import ServiceCentreReport


class ServiceCentreDetailsReport(ServiceCentreReport):
    def __init__(self, filters=None):
        super().__init__(filters)

    def fetch_data(self):
        query = """
            SELECT 
                name AS 'service_centre_name',
                address AS 'service_centre_address',
                phone_no AS 'service_centre_phone_no',
                upi_id AS 'service_centre_upi_id',
                ifsc_code AS 'service_centre_ifsc_code',
                bank_account_no AS 'service_centre_bank_account_no',
                bank_name AS 'service_centre_bank_name',
                kilometer_category AS 'service_centre_kilometer_category',
                fixed_rate AS 'service_centre_fixed_rate',
                per_kilometer_rate AS 'service_centre_per_kilometer_rate',
                pincode AS 'service_centre_pincode'
            FROM 
                `tabService Centre`
        """
        raw_data = frappe.db.sql(query, as_dict=True)
        return raw_data

    def fetch_columns(self):
        return [
            {
                "label": "Service Centre Name",
                "fieldname": "service_centre_name",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "label": "Address",
                "fieldname": "service_centre_address",
                "fieldtype": "Data",
                "width": 250,
            },
            {
                "label": "Phone No",
                "fieldname": "service_centre_phone_no",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": "UPI ID",
                "fieldname": "service_centre_upi_id",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "label": "IFSC Code",
                "fieldname": "service_centre_ifsc_code",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": "Bank Account No",
                "fieldname": "service_centre_bank_account_no",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": "Bank Name",
                "fieldname": "service_centre_bank_name",
                "fieldtype": "Data",
                "width": 200,
            },
            {
                "label": "Kilometer Category",
                "fieldname": "service_centre_kilometer_category",
                "fieldtype": "Data",
                "width": 180,
            },
            {
                "label": "Fixed Rate",
                "fieldname": "service_centre_fixed_rate",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "label": "Per Kilometer Rate",
                "fieldname": "service_centre_per_kilometer_rate",
                "fieldtype": "Currency",
                "width": 120,
            },
            {
                "label": "Pincode",
                "fieldname": "service_centre_pincode",
                "fieldtype": "Data",
                "width": 100,
            },
        ]

    def get_message(self):
        return """
            <h1 style='text-align:center; color:orange;'>Service Centre Details Report</h1>
        """

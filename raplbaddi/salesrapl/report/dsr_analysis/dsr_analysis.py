# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt
import frappe
from datetime import datetime
from frappe.utils import dateutils


class getAnalysis:
    def __init__(self, filters):
        self.filters = filters
        self._get_data()

    # Use to get the columns
    def get_columns(self):
        columns = [
            {"fieldname": "Sales_Person","label": ("Sales Person"),"fieldtype": "Data",},
            {"fieldname": "party", "label": ("Party Name"), "fieldtype": "Data"},
            {"fieldname": "Date", "label": ("Date Of Visit"), "fieldtype": "Date"},
            {"fieldname": "Remarks", "label": ("Remarks"), "fieldtype": "Data"},
            {"fieldname": "Visit", "label": ("No of times Visited"),"fieldtype": "Int", }
        ]
        return columns

    def _get_data(self):
        query = f"""
		SELECT  SUBSTRING_INDEX(DSRA.name,' ',2) AS Sales_Person,
		DSL.party_name as party,
		SUBSTRING_INDEX(DSRA.creation," ",1) as 'Date',
		DSL.remarks as Remarks,
		1 as Visit
		from  `tabDaily Sales Report By Admin` as DSRA
		JOIN `tabDaily Sales Lead` as DSL ON DSRA.name = DSL.parent 
		ORDER BY Sales_Person ASC
				"""
        result = frappe.db.sql(query, as_dict=True)
        self.data = result
    def get_filtered_data(self):
        self.filters.start_date = self.filters.get('start_date')
        self.filters.sales_person = self.filters.get('sales_person')
        self.filters.end_date = self.filters.get('end_date')
        self.filterd_data = []
        for i in self.data:
            if (not self.filters.sales_person or i['Sales_Person'] == self.filters.sales_person)and(not self.filters.start_date or i['Date'] >= self.filters.start_date) and (not self.filters.end_date or i['Date'] <= self.filters.end_date):
                self.filterd_data.append(i)
        return self.filterd_data

    


def execute(filters=None):
    analysis = getAnalysis(filters)
    columns, data = [], []
    return analysis.get_columns(), analysis.get_filtered_data()

# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
import locale
from ..data.dsra import DSRA
from datetime import datetime


class expenseAnalysis:
    def __init__(self, filters):
        self.filters = filters
        print(self.filters)
        self.data = {}
        self.set_data()

    def format_date(self, date_str):
        return datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else None

    def set_data(self):
        self.data['dsra'] = DSRA().get_dsra()

    def format_no(self, num):
        locale.setlocale(locale.LC_ALL, "")
        return locale.format_string("%.0f", num, grouping=True).replace(",", ",", 1)

    def get_columns(self):
        columns = [
            {
                "fieldname": "date",
                "label": ("Date Of Visted"),
                "fieldtype": "Date",
                "width": 130,
            },
            {
                "fieldname": "sales_person",
                "label": ("Sales_Person"),
                "fieldtype": "Data",
                "width": 130,
            },
            {
                "fieldname": "total_amount",
                "label": ("Amount"),
                "fieldtype": "Currency",
                "width": 140,
            },
        ]
        return columns

    def get_filtered_data(self):
        sales_person = self.filters.get("sales_person")
        from_date = self.format_date(self.filters.get("from_date"))
        to_date = self.format_date(self.filters.get("to_date"))
        self.filtered_data = []

        for i in self.data['dsra']:
            if (not sales_person or i["sales_person"] == sales_person) and \
            (not from_date or i["date"] >= from_date) and \
            (not to_date or i["date"] <= to_date):
                self.filtered_data.append(i)

        self.filtered_data.sort(key=lambda k: k['date'])
        return self.filtered_data

    def get_count(self):
        return len(self.filtered_data)

    def get_total_amount(self):
        ret = 0
        for data in self.filtered_data:
            ret += data.total_amount
        print(ret)
        return ret

    def get_msg(self):
        count = self.get_count()
        amount = self.get_total_amount()
        sales_person = self.filters.sales_person
        return f"""
        <div style="display: flex; justify-content: space-between;">
            <h3>Visits: {count}</h3>
            <h3>{sales_person}</h3>
            <h3>Expense: ₹{self.format_no(amount)}</h3>
            <h3>₹/Day: ₹{self.format_no(amount//count) if count != 0 else 0}</h3>
        </div>"""


def execute(filters=None):
    analysis = expenseAnalysis(filters)
    columns, data = [], []
    return analysis.get_columns(), analysis.get_filtered_data(), analysis.get_msg()

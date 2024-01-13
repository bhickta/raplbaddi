# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime


class payment:
    def __init__(self, filters) -> None:
        self.filters = filters
        self.process_filters()
        self.get_conditions()
        self.get_data()
        self.set_paid()

    def process_filters(self):
        self.filters.end_date = datetime.strptime(self.filters.end_date, "%Y-%m-%d").date()
        self.filters.start_date = datetime.strptime(self.filters.start_date, "%Y-%m-%d").date()

    def get_query(self):
        from .data import get_query

        self.query = get_query(self.filters, self.conditions)

    def get_data(self):
        self.get_query()
        result = frappe.db.sql(self.query, as_dict=True)
        self.data = result

    def get_conditions(self):
        self.conditions = "1 "
        if self.filters.payment_done:
            self.conditions += f" and i.payment_done = '{self.filters.payment_done}'"
        if self.filters.customer_confirmation:
            self.conditions += (
                f" and i.customer_confirmation = '{self.filters.customer_confirmation}'"
            )
        if self.filters.service_delivered:
            self.conditions += (
                f" and i.service_delivered = '{self.filters.service_delivered}'"
            )

    def filtered_data(self):
        self.filtered_data = []
        for data in self.data:
            data.amount = int(data.amount)
            data.ifsc = data.ifsc
            data.date = data.date.date()
            data.per_complaint = int(data.amount / data.count)
            if (
                (
                    not self.filters.service_centre
                    or data.service_centre == self.filters.service_centre
                )
                and (
                    not self.filters.start_date or data.date >= self.filters.start_date
                )
                and (not self.filters.end_date or data.date <= self.filters.end_date)
            ):
                self.filtered_data.append(data)
        return self.filtered_data

    def get_columns(self):
        from .columns import get_columns

        return get_columns(self.filters)

    def get_count(self):
        self.counts = len(self.filtered_data)

    def get_total_amount(self):
        self.ret = 0
        for data in self.filtered_data:
            self.ret += data.amount
        self.payment = int(self.ret)

    def get_account_details(self):
        if self.filters.service_centre:
            self.account_no = self.filtered_data[0]['account_no']
            self.bank_ifsc = self.filtered_data[0]['ifsc']
            self.bank_name = self.filtered_data[0]['bank']
            self.upi = self.filtered_data[0]['upi']
          
        else:
            self.account_no,self.bank_ifsc,self.bank_name,self.upi = None,None,None,None

    def get_msg(self):
        self.get_count()
        self.get_total_amount()
        self.get_account_details()
        ret = f"""
        <div style="display: flex; justify-content: space-between;">
            <h2>Complaints : {self.counts}</h2>
            <h2> {"-" if not self.filters.service_centre else self.filters.service_centre}</h2>
            <h2>Amount : {self.payment}</h2>
        </div> <br>
                """
        if self.filters.service_centre:
            ret += f"""
            <div style="display: flex; justify-content: space-between;">
            <h4>Bank : {self.bank_ifsc}</h4>
            <h4>Account No : {self.account_no}</h4>
            <h4>IFSC : {self.bank_name}</h4>
            <h4>UPI Id : {self.upi}</h4>
        </div>
        """
        return ret

    def set_paid(self):
        if self.filters.service_centre :
            pass
    

def execute(filters=None):
    payee = payment(filters)
    columns, data = [], []
    return payee.get_columns(), payee.filtered_data(),payee.get_msg() if not filters.group_by_sc else ""



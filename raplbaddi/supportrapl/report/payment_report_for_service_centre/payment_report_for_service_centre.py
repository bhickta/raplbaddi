# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from raplbaddi.raplbaddi.report.utils.service_centre import ServiceCentreReport


class ServiceCentrePaymentReport(ServiceCentreReport):
    def __init__(self, filters) -> None:
        self.filters = filters

    def get_query(self, grouped):
        select_fields = (
            """
            COUNT(i.name) AS count,
            SUM(i.amount) AS amount,
            SUM(i.kilometer) AS kilometer
            """
            if grouped
            else """
            1 AS count,
            i.name AS complaint_no,
            i.amount AS amount,
            i.kilometer AS kilometer
            """
        )

        common_fields = """
            CASE 
                WHEN i.custom_creation_date THEN DATE(i.custom_creation_date) 
                ELSE DATE(i.creation) 
            END AS date,
            j.service_centre_name AS service_centre,
            j.bank_name AS bank,
            j.bank_account_no AS account_no,
            j.ifsc_code AS ifsc,
            j.upi_id AS upi,
            i.payment_done AS payment_status,
            i.service_delivered AS service_delivered,
            i.customer_confirmation
        """

        query = f"""
            SELECT 
                {select_fields},
                {common_fields}
            FROM 
                `tabIssueRapl` AS i
            LEFT JOIN 
                `tabService Centre` AS j 
            ON 
                i.service_centre = j.service_centre_name
            WHERE 
                i.service_centre NOT IN %(excluded_service_centres)s
        """
       
        return query


    def get_data(self):

        params = {
            "excluded_service_centres": tuple(
                [
                    "Geo Appliances", 
                    "Amit Company Inside", 
                    "Amit Company Outside", 
                    "HIMANSHU COMPANY"
                ]
            ),
            "payment_done": self.filters.get("payment_done"),
            "customer_confirmation": self.filters.get("customer_confirmation"),
            "service_delivered": self.filters.get("service_delivered"),
            "start_date": self.filters.get("start_date"),
            "end_date": self.filters.get("end_date"),
            "allowed_service_centres": tuple(self.allowed_service_centres)
            if self.allowed_service_centres
            else None,
        }
        grouped=self.filters.get("group_by_sc")
        
        query = self.get_query(grouped)

        if params.get("payment_done"):
            query += " AND i.payment_done = %(payment_done)s"
        if params.get("customer_confirmation"):
            query += " AND i.customer_confirmation = %(customer_confirmation)s"
        if params.get("service_delivered"):
            query += " AND i.service_delivered = %(service_delivered)s"
        if params["start_date"] and params["end_date"]:
            query += " AND i.custom_creation_date BETWEEN %(start_date)s AND %(end_date)s"
        if params.get("allowed_service_centres"):
            query += " AND i.service_centre IN %(allowed_service_centres)s"

        if grouped:
            query += " GROUP BY i.service_centre"
        query += " ORDER BY amount DESC, count DESC"

        self.data = frappe.db.sql(query, params, as_dict=True)

    def fetch_data(self):
        self.get_data()
        self.filtered_data = self.data
        return self.filtered_data

    def get_column(self):
        return self.get_columns()

    def fetch_columns(self):
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
            self.account_no = self.filtered_data[0]["account_no"]
            self.bank_ifsc = self.filtered_data[0]["ifsc"]
            self.bank_name = self.filtered_data[0]["bank"]
            self.upi = self.filtered_data[0]["upi"]

        else:
            self.account_no, self.bank_ifsc, self.bank_name, self.upi = (
                None,
                None,
                None,
                None,
            )

    def fetch_message(self):
        return self.get_msg()

    def get_msg(self):
        return ""
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


def execute(filters=None):
    payee = ServiceCentrePaymentReport(filters)
    return payee.run()

# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext import get_default_company


class SNCStockEntry(Document):
    def before_save(self):
        date = self.get("date_of_entry")
        transfer(items=self.items,name=self.get("name"), date=date)


@frappe.whitelist()
def transfer(items, name, date):
    """Helper function to make a Stock Entry
    :items: Item to be moved
    """
    s = frappe.new_doc("Stock Entry")
    s.company = get_default_company()
    s.stock_entry_type = "Geyser Changed"
    s.serial_no_changing_entry = name
    s.set_posting_time = 1
    s.posting_date = date

    # items
    for item in items:
        s.append('items', {
            "item_code": item.item_code,
            "qty": item.qty,
            "s_warehouse": item.f_warehouse,
            "t_warehouse": item.t_warehouse,
            "is_finished_item": 1,
        })

    # insert
    s.insert()
    s.submit()
    return s


@frappe.whitelist()
def get_production_data(serial_number):
    items = frappe.db.sql(f"""
		SELECT DISTINCT gpet.item_name, gpet.brand, gpe.date_of_production
		FROM `tabGeyser Production Entry Table` as gpet JOIN `tabGeyser Production Entry` as gpe ON gpe.name = gpet.parent
		WHERE '{serial_number}' BETWEEN from_serial AND to_serial
	""", as_dict=True)
    return items

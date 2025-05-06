# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext import get_default_company

class ElementProductionEntry(Document):
    def on_submit(self):
        date = self.get("date_of_production")
        manufacture(items=self.get("items"), name=self.get("name"), date=date)


@frappe.whitelist()
def manufacture(items, name, date):
    """Helper function to make a Stock Entry
    :items: Item to be moved
    """
    s = frappe.new_doc("Stock Entry")
    s.company = get_default_company()
    s.stock_entry_type = "Element Manufactured"
    s.element_production_entry = name
    s.set_posting_time = 1
    s.posting_date = date

    # items
    for item in items:
        s.append('items', {
            "item_code": item.item,
            "qty": item.qty_tested,
            "t_warehouse": 'Element Section' + " - RAPL",
            "is_finished_item": 1,
        })

    # insert
    s.insert()
    s.submit()
    return s

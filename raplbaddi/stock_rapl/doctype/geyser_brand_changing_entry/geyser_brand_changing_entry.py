# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from erpnext import get_default_company


class GeyserBrandChangingEntry(Document):
    def on_submit(self):
        transfer(
            items=self.get("items"),
            name=self.get("name"),
            date=self.get("posting_date"),
            time=self.get("posting_time"),
        )


@frappe.whitelist()
def transfer(items, name, date, time):
    """Helper function to make a Stock Entry
    :items: Item to be moved
    """
    s = frappe.new_doc("Stock Entry")
    s.company = get_default_company()
    s.stock_entry_type = "Geyser Brand Change"
    s.geyser_brand_changing_entry = name
    s.set_posting_time = 1
    s.posting_date = date
    s.posting_time = time
    # items
    for item in items:
        if item.new_brand == item.old_brand:
            frappe.throw("Old brand can't be same as new brand")
        s.append(
            "items",
            {
                "item_code": item.item,
                "qty": item.qty,
                "is_finished_item": 1,
                "t_warehouse": item.new_brand + " - RAPL",
                "s_warehouse": item.old_brand + " - RAPL",
            },
        )
    # insert
    s.insert()
    s.submit()
    return s

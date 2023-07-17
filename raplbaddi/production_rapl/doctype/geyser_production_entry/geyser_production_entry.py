# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GeyserProductionEntry(Document):
	def on_submit(self):
		date = self.get("date_of_production")
		manufacture(items=self.get("items"), name=self.get("name"), date=date)

@frappe.whitelist()
def manufacture(items, name, date):
	"""Helper function to make a Stock Entry
	:items: Item to be moved
	"""
	s = frappe.new_doc("Stock Entry")
	s.company = "Real Appliances Private Limited"
	s.stock_entry_type = "Geyser Manufactured"
	s.production_entry = name
	s.set_posting_time = 1
	s.posting_date = date
	
	# items
	for item in items:
		s.append('items', {
			"item_code": item.item,
			"qty": item.qty,
			"t_warehouse": item.brand + " - RAPL",
			"is_finished_item": 1,
		})

	# insert
	s.insert()
	s.submit()
	return s
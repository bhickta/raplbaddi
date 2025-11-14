# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
import ast
import json
from frappe.model.document import Document

class ProductionEntry(Document):
	pass

@frappe.whitelist()
def make_production_entry(**args):
	print(args['entry_date'])
	item_dict_list = ast.literal_eval(args['items'])
	stock_entry_type = args['stock_entry_type']
	if stock_entry_type and stock_entry_type == 'Element Receipt':
		for item_dict in item_dict_list:
			e = frappe.new_doc('Production Entry')
			e.total_quantity = item_dict['qty']
			e.element_type = item_dict['item_code']
			e.insert()
	return "Done"
# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ContractorRateList(Document):
	def validate(self):
		print(get_contractor_item_rates('Dinbandhu', 'G13A'))

def get_contractor_item_rates(contractor, item_code):
	rate = frappe.get_value('Contractor Rates Details', {
		'parent': contractor, 'item_code': item_code
	}, ['rates'])
	return rate
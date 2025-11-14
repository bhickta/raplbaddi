# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ContractorRateList(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from raplbaddi.contract_manufacturing.doctype.contractor_rate_item.contractor_rate_item import ContractorRateItem

		contractor: DF.Link
		contractor_name: DF.Data | None
		disabled: DF.Check
		items: DF.Table[ContractorRateItem]
		naming_series: DF.Literal["CRL-.####."]
	# end: auto-generated types
	def validate(self):
		print(get_contractor_item_rates('Dinbandhu', 'G13A'))

def get_contractor_item_rates(contractor, item_code):
	rate = frappe.get_value('Contractor Rates Details', {
		'parent': contractor, 'item_code': item_code
	}, ['rates'])
	return rate
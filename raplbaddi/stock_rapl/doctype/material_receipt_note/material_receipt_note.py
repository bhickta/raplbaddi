# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from raplbaddi.utils import make_fields_set_only_once

class MaterialReceiptNote(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from raplbaddi.stock_rapl.doctype.material_receipt_note_item.material_receipt_note_item import MaterialReceiptNoteItem

		amended_from: DF.Link | None
		branch: DF.Link
		customer: DF.Link | None
		date: DF.Date | None
		invoice_received: DF.Check
		items: DF.Table[MaterialReceiptNoteItem]
		naming_series: DF.Literal["MRN-.YY.-.#"]
		supplier: DF.Link | None
		supplier_invoice_number: DF.Data | None
		supplier_name: DF.Data | None
	# end: auto-generated types
	pass

	def before_insert(self):
		self.set_naming_series()
		
	def set_naming_series(self):
		naming_series_map = {
			"Real Appliances Private Limited": {
				False: "MRN-.YY.-RAPL-.####",
			},
			"Red Star Unit 2": {
				False: "MRN-.YY.-RSI-.####",
			}
		}

		if self.branch in naming_series_map:
			self.naming_series = naming_series_map[self.branch][False]

	def validate(self):
		self.validate_naming_series()

	def validate_naming_series(self):
		make_fields_set_only_once(self, ["branch"])
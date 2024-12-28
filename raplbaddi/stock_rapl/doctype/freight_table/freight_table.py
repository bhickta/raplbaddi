# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class FreightTable(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		type: DF.Literal["Basic", "Big Vehicle", "Dala", "Half Dala", "Double Height", "Point", "Via"]
	# end: auto-generated types
	pass

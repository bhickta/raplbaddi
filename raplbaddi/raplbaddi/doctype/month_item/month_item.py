# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class MonthItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		month: DF.Literal["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		value: DF.Int
		year: DF.Int
	# end: auto-generated types
	pass

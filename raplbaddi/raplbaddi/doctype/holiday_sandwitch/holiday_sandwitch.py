# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class HolidaySandwitch(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		designation: DF.Link
		minimum_weekly_attendance: DF.Int
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
	# end: auto-generated types
	pass

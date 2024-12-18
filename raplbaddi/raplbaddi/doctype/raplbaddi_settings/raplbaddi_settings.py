# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class RaplbaddiSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from raplbaddi.raplbaddi.doctype.holiday_sandwitch.holiday_sandwitch import HolidaySandwitch

		holiday_sandwitch: DF.Table[HolidaySandwitch]
	# end: auto-generated types
	pass

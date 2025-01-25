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
		from raplbaddi.raplbaddi.doctype.holiday_sandwich.holiday_sandwich import HolidaySandwich

		holiday_sandwich: DF.Table[HolidaySandwich]
		is_internal_receipt_for_service_centre_on_dn: DF.Check
		service_centre_group: DF.Link | None
	# end: auto-generated types
	pass

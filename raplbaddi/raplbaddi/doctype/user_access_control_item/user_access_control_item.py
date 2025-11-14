# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class UserAccessControlItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		allow: DF.Link
		applicable_for: DF.Link | None
		apply_to_all_doctypes: DF.Check
		for_value: DF.DynamicLink
		is_default: DF.Check
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		permission: DF.Data | None
	# end: auto-generated types
	pass

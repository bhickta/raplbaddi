# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Remark(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		description: DF.SmallText | None
		is_disabled: DF.Check
		product: DF.Data | None
		title: DF.Data | None
	# end: auto-generated types
	pass

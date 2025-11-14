# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Sticker(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		nature: DF.Literal["Common", "Not Common"]
		sample: DF.AttachImage | None
		source: DF.Link
		sticker_type: DF.Link
		title: DF.Data
	# end: auto-generated types
	pass

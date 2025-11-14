# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class StickerItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		capacity: DF.Link | None
		model: DF.Link | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		sticker: DF.Link
		sticker_type: DF.Literal["", "Logo", "Lahar", "ISI", "Specification Plate", "Five Star", "Box Model Sticker"]
	# end: auto-generated types
	pass

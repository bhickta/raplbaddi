# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SubIssue(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from raplbaddi.raplbaddi.doctype.model_item.model_item import ModelItem

		description: DF.SmallText | None
		is_disabled: DF.Check
		issue_type: DF.Link
		model_items: DF.Table[ModelItem]
		product: DF.Literal["Geyser", "Desert Air Cooler"]
		title: DF.Data
	# end: auto-generated types
	pass

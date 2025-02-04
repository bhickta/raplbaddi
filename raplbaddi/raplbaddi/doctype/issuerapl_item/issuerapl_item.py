# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class IssueRaplItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		issue_type: DF.Link
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		sub_issue: DF.Link | None
	# end: auto-generated types
	pass

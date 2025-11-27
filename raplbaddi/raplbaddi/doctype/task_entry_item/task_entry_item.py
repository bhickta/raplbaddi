# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TaskEntryItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		assigned_to: DF.Link | None
		details: DF.SmallText | None
		due_date: DF.Date | None
		employee_full_name: DF.ReadOnly | None
		frequency: DF.Literal["Daily", "Weekly", "Monthly", "One-time"]
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		priority: DF.Literal["Low", "Medium", "High"]
		remarks: DF.SmallText | None
		status: DF.Literal["Open", "In Progress", "Completed"]
		task_name: DF.Data | None
		task_type: DF.Literal["Regular", "Occasional"]
		when_completed: DF.Date | None
	# end: auto-generated types
	pass

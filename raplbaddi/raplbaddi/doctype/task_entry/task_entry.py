# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TaskEntry(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from raplbaddi.raplbaddi.doctype.task_entry_item.task_entry_item import TaskEntryItem

		amended_from: DF.Link | None
		date_of_task_entry: DF.Date | None
		employee_name: DF.ReadOnly | None
		for_which_user: DF.Link | None
		general_notes: DF.SmallText | None
		period: DF.Literal["Daily", "Weekly", "Monthly"]
		status: DF.Literal["Open", "Closed"]
		task_entry_item: DF.Table[TaskEntryItem]
	# end: auto-generated types
	pass

def on_submit(self):
    # For every row in child table, create an assignment
    for row in self.task_entry_item:
        if row.assigned_to:
            self.assign_to_user(row)
            

def assign_to_user(self, row):
    # Create an Assignment record
    frappe.get_doc({
        "doctype": "Assignment",
        "assigned_to": row.assigned_to,
        "reference_doctype": "Task Entry",
        "reference_name": self.name,
        "priority": "Medium",
        "description": f"Task Assigned: {row.task_name}"
    }).insert(ignore_permissions=True)


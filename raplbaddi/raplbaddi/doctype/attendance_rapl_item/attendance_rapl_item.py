# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AttendanceRaplItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attendance: DF.Literal["Present", "Absent", "On Leave", "Half Day", "Work From Home"]
		check_in: DF.Time
		check_out: DF.Time
		date: DF.Date | None
		day: DF.Data | None
		duration: DF.Duration | None
		employee: DF.Link
		employee_name: DF.Data
		end_time: DF.Time | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		shift_type: DF.Link
		start_time: DF.Time | None
	# end: auto-generated types
	pass

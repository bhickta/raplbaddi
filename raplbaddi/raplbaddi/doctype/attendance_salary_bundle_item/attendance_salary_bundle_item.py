# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class AttendanceSalaryBundleItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attendance: DF.Literal["Present", "Absent", "On Leave", "Half Day", "Work From Home"]
		attendance_item: DF.Data | None
		attendance_rapl: DF.Link | None
		date: DF.Date | None
		duration: DF.Duration | None
		hourly_rate: DF.Float
		is_holiday: DF.Check
		monthly_salary: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		salary: DF.Float
		shift_duration: DF.Duration | None
		shift_type: DF.Link | None
	# end: auto-generated types
	pass

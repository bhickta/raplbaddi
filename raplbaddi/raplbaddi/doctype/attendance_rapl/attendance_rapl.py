# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import time_diff_in_seconds


class AttendanceRapl(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from raplbaddi.raplbaddi.doctype.attendance_rapl_item.attendance_rapl_item import AttendanceRaplItem

		amended_from: DF.Link | None
		branch: DF.Link
		date: DF.Date
		department: DF.Link
		items: DF.Table[AttendanceRaplItem]
	# end: auto-generated types
	pass

	def autoname(self):
		"""Auto name the document using branch, department, and date."""
		branch_name = self.branch
		if self.branch == "Real Appliances Private Limited":
			branch_name = "RAPL"
		elif self.branch == "Red Star Unit 2":
			branch_name = "RSI"

		department_abbreviation = frappe.get_value("Department", self.department, "abbriviation") or self.department[:3]
		formatted_date = self.date

		self.name = f"{branch_name} {department_abbreviation} {formatted_date}"

	def validate(self):
		self.validate_employee_duration()
	
	def validate_employee_duration(self):
		for item in self.items:
			if item.duration and item.duration < 0:
				frappe.throw(_("Duration of {0} must be greater than or equal to 0").format(item.name))
			item.duration = time_diff_in_seconds(item.check_out, item.check_in)
			if item.attendance == "Absent":
				item.duration = 0
				item.check_in = item.check_out = "06:00:00"
			if not item.duration:
				item.attendance = "Absent"
			else:
				item.attendance = "Present"
			item.date = self.date

@frappe.whitelist()
def get_employee_shift_info(doc):
	doc = frappe.parse_json(doc)
	filters = {
		'status': 'Active',
	}
	for field in ["branch", "department"]:
		if field in doc:
			filters.update({
				field: doc.get(field)
			})
	
	employees = frappe.get_all('Employee', fields=['name', 'employee_name', 'default_shift'], filters=filters)
	shift_info = []

	for employee in employees:
		shift = frappe.get_value('Shift Type', employee.default_shift, ['start_time', 'end_time'])
		if shift:
			start_time = shift[0]
			end_time = shift[1]

			shift_info.append({
				'employee': employee.name,
				'employee_name': employee.employee_name,
				'default_shift': employee.default_shift,
				'start_time': start_time,
				'end_time': end_time,
			})

	return shift_info

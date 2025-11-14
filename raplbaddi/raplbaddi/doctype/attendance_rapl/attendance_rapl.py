# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _
from frappe.utils import time_diff_in_seconds, get_datetime, generate_hash
from datetime import datetime, timedelta
import calendar
from raplbaddi.raplbaddi.doctype.attendance_salary_bundle.attendance_salary_bundle import Holiday

class AttendanceRapl(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from raplbaddi.raplbaddi.doctype.attendance_rapl_item.attendance_rapl_item import AttendanceRaplItem

		amended_from: DF.Link | None
		branch: DF.Link | None
		date: DF.Date
		department: DF.Link | None
		employee: DF.Link | None
		is_marketing_employee_included: DF.Check
		items: DF.Table[AttendanceRaplItem]
		status: DF.Literal["", "Audited"]
	# end: auto-generated types
	pass

	def autoname(self):
		"""Auto name the document using branch, department, and date."""
		branch_name = self.branch
		if self.branch == "Real Appliances Private Limited":
			branch_name = "RAPL"
		elif self.branch == "Red Star Unit 2":
			branch_name = "RSI"

		department_abbreviation = frappe.get_value("Department", self.department, "abbriviation") or None
		if not department_abbreviation:
			department_abbreviation = generate_hash(length=4)
		formatted_date = self.date

		self.name = f"{branch_name} {department_abbreviation} {formatted_date}"

	def validate(self):
		self.validate_employee_duration()
		self.add_attendance_for_sales_based_on_dsra()
		self.set_day_of_the_week()
		self.is_holiday()
	
	def remove_lunch_time(self, row, lunch_end):
		checkout_time = row.check_out

		if not isinstance(checkout_time, timedelta):
			try:
				hours, minutes, seconds = map(int, str(checkout_time).split(":"))
				checkout_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
			except ValueError:
				frappe.throw(f"Invalid checkout time format: {checkout_time}")

		if checkout_time > lunch_end:
			lunch_time_duration = 0.5 * 60 * 60
			row.duration -= lunch_time_duration
   
	def add_attendance_for_sales_based_on_dsra(self):
		if not self.is_marketing_employee_included:
			return
		dsra_list = frappe.get_all(
			"Daily Sales Report By Admin",
			filters={
				"docstatus": 1,
				"date": ["=", self.date],
			},
			fields=["sales_person"],
			pluck="sales_person",
		)
		for sp in dsra_list:
			employee = frappe.get_doc("Sales Person", sp).employee
			if not employee:
				frappe.throw("Sales Person {0} should be linked with {1} in Sales Person Master".format(sp, "Employee"))
			employee_doc = frappe.get_doc("Employee", employee)
			if employee_doc.default_shift not in ["Marketing"]:
				frappe.throw("Default Shift Type must be Marketing in {0}: {1} Master".format(employee_doc.employee, employee_doc.employee_name))
			if employee_doc.name in [item.employee for item in self.items]:
				continue
			if employee:
				self.append(
					"items",
					{
						"employee": employee_doc.name,
						"employee_name": employee_doc.employee_name,
						"check_in": "06:00:00",
						"shift_type": "Marketing",
						"check_out": "06:00:00",
						"attendance": "Present",
						"duration": 0,
					}
				)

	def validate_employee_duration(self):
		for item in self.items:
			if item.shift_type in ["Marketing"]:
				continue
			if item.duration and item.duration < 0:
				frappe.throw(_("Duration of {0} must be greater than or equal to 0").format(item.name))
			item.duration = time_diff_in_seconds(item.check_out, item.check_in)
			self.remove_lunch_time(item, timedelta(hours=13, minutes=30, seconds=0))
			if item.attendance == "Absent":
				item.duration = 0
				item.check_in = item.check_out = "06:00:00"
			if not item.duration:
				item.attendance = "Absent"
			else:
				item.attendance = "Present"
			item.date = self.date

	def before_submit(self):
		if self._action == "cancel":
			return
		mandatory = [{
			"status": "Audited",
		}]
		for item in mandatory:
			for field, value in item.items():
				if not self.get(field) == value:
					frappe.throw(f"{field.capitalize()} must be {value}")
     
	def set_day_of_the_week(self):
		for item in self.items:
			if isinstance(item.date, str):
				item.date = datetime.strptime(item.date, "%Y-%m-%d").date()
			item.day = calendar.day_name[item.date.weekday()]
   
	def is_holiday(self):
		for item in self.items:
			item.is_holiday = Holiday.is_holiday(item.employee, item.date)

import re

def natural_sort_key(value):
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split(r'(\d+)', value or "")
    ]

@frappe.whitelist()
def get_employee_shift_info(doc):
	doc = frappe.parse_json(doc)
	filters = {
		'status': 'Active',
		'designation': ["NOT IN", ["Contractor"]],
		'default_shift': ["NOT IN", ["Marketing"]],
	}

	for field in ["branch", "department"]:
		if bool(doc.get(field)):
			filters.update({
				field: doc.get(field)
			})

	if doc.get('employee'):
		filters.update({
			'name': doc.get('employee')
		})
 
	employees = frappe.get_all('Employee', fields=['name', 'employee_name', 'default_shift', 'serial_number'], filters=filters)
	employees.sort(key=lambda x: natural_sort_key(x['serial_number']))
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

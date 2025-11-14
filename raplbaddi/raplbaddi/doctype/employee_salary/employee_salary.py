# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class EmployeeSalary(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from raplbaddi.raplbaddi.doctype.month_item.month_item import MonthItem

		amended_from: DF.Link | None
		employee: DF.Link
		employee_name: DF.Data | None
		items: DF.Table[MonthItem]
		year: DF.Int
	# end: auto-generated types
	pass

	def validate(self):
		for item in self.items:
			item.year = self.year

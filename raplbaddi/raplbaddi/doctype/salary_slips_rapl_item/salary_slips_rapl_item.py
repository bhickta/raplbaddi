# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class SalarySlipsRaplItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		attendance_salary_bundle: DF.Link | None
		employee: DF.Link | None
		employee_name: DF.Data | None
		holidays: DF.Float
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		salary: DF.Float
	# end: auto-generated types
	pass

# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PaperName(Document):
	def get_name(self):
		paper_name_sequence = "-".join([item.capacity for item in self.items])
		return f'{self.paper_type[0:1]}-{paper_name_sequence}'
	def autoname(self):
		name = self.get_name()
		print(name)
		# if not frappe.db.exists('Paper Name', self.name):
		self.name = name
		return
		# else:
		# 	if self.name != self.get_name():
		# 		frappe.rename_doc("Paper Name",
		# 							self.name, name)
	# def on_update(self):
	# 	self.autoname()
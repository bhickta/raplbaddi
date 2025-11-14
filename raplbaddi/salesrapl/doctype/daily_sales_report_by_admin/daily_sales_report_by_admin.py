# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class DailySalesReportByAdmin(Document):
	def validate(self):
		self.set_km_travelled()
		self.set_total_amount()
	
	def set_km_travelled(self):
		starting_reading = self.start_reading or 0
		ending_reading = self.end_reading or 0
		if starting_reading > ending_reading:
			frappe.throw("Start Reading should be less than End Reading")
		self.km_travelled = ending_reading - starting_reading
		self.amount_for_travel = self.km_travelled * self.get_travel_rate()
  
	def get_travel_rate(self):
		rate = frappe.get_cached_value("Sales Person", self.sales_person, "travel_rate")
		return rate
  
	def set_total_amount(self):
		amt = self.get('amount_for_travel', 0)
		if self.get('daily_sales_expenses_by_admin', []):
			for x in self.get('daily_sales_expenses_by_admin', []):
				amt += x.amount
		self.total_amount = amt

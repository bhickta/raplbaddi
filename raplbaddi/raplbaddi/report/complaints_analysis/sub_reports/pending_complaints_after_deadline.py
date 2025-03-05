# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from raplbaddi.raplbaddi.report.utils.service_centre import ServiceCentreReport


class DaysDeadline(ServiceCentreReport):
	def __init__(self,filters):
		self.filters = filters
		self.count = 0
  
	def fetch_data(self):
		query = f"""
			SELECT 
				name,
				custom_creation_date ,
				CURDATE() as 'today',
				DATEDIFF(CURDATE(),custom_creation_date) as 'days_diff'
			FROM 
				tabIssueRapl
			WHERE 
				DATEDIFF(CURDATE(),custom_creation_date) >3 AND service_delivered = "No"
				and docstatus != 2
			ORDER BY
				custom_creation_date

		"""
    
		result = frappe.db.sql(query, as_dict=True)
		self.count = len(result)   
		data = result
		return data

	def fetch_columns(self):
		columns = [
			{
				'fieldname':'name',
				'label':'Name',
				'fieldtype':'Link',
				'options': 'IssueRapl',
				'width':'310'
			},
			{
				'fieldname':'custom_creation_date',
				'label':'Complaint Register Date',
				'fieldtype':'Date',
				'width':'310'
			},
			{
				'fieldname':'days_diff',
				'label':'Days Difference',		
				'fieldtype':'Int',
				'width':'250'
			}
		]
		return columns

	def fetch_message(self):
		return f'''
			<h1 style = 'text-align:center; color:orange;'>No. of pending complaints after deadline are : {self.count} </h1>
  		'''

// // Copyright (c) 2023, Nishant Bhickta and contributors
// // For license information, please see license.txt

frappe.query_reports["DSR Analysis"] = {
"filters" : [
	
	{
		'fieldname':'sales_person',
		'label': __('Sales Person'),
		'fieldtype':'Link',
		'options':'Sales Person'
	},
	{
		'fieldname': 'start_date',
		'label': __('Start Date'),
		'fieldtype': 'Date'
	},
	{
		'fieldname': 'end_date',
		'label': __('End Date'),
		'fieldtype': 'Date'
	}	
]
}
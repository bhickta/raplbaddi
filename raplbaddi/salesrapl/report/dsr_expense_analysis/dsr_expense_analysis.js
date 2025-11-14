// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt



frappe.query_reports["DSR Expense Analysis"] = {
	onload: function(report) {
		// arr = frappe.datetime.get_today().split("-")
        // arr.push("0" + (parseInt(arr.pop()) - 1))
        // yesterday = arr.join("-") 

        report.page.add_inner_button(__("Today"), function() {
            frappe.query_report.get_filter('from_date').set_value(frappe.datetime.get_today());
            frappe.query_report.get_filter('to_date').set_value(frappe.datetime.get_today());
        }, "Range");
        // report.page.add_inner_button(__("Yesterday"), function() {
        //     frappe.query_report.get_filter('from_date').set_value(yesterday);
        //     frappe.query_report.get_filter('to_date').set_value(yesterday);
        // }, "Range");
        report.page.add_inner_button(__("Week"), function() {
            frappe.query_report.get_filter('from_date').set_value(frappe.datetime.week_start());
            frappe.query_report.get_filter('to_date').set_value(frappe.datetime.week_end());
        }, "Range");
		report.page.add_inner_button(__("Month"), function() {
			frappe.query_report.get_filter('from_date').set_value(frappe.datetime.month_start());
			frappe.query_report.get_filter('to_date').set_value(frappe.datetime.month_end());
		}, "Range");
		report.page.add_inner_button(__("Quarter"), function() {
			frappe.query_report.get_filter('from_date').set_value(frappe.datetime.quarter_start());
			frappe.query_report.get_filter('to_date').set_value(frappe.datetime.quarter_end());
		}, "Range");
        report.page.add_inner_button(__("Year"), function() {
            frappe.query_report.get_filter('from_date').set_value(frappe.datetime.year_start());
            frappe.query_report.get_filter('to_date').set_value(frappe.datetime.year_end());
        }, "Range");
    },
	"filters": [
			{
				'fieldname':'sales_person',
				'label':__('Sales Person'),
				'fieldtype':'Link',
				'options':'Sales Person'

			},
			{
				'fieldname': 'from_date',
				'label': __('Start Date'),
				'fieldtype': 'Date',
			},
			{
				'fieldname': 'to_date',
				'label': __('End Date'),
				'fieldtype': 'Date',
			}					
		]
};

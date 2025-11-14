// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Delivery Notes All Salesmanwise"] = {
	onload: function(report) {
		arr = frappe.datetime.get_today().split("-")
        arr.push("" + (parseInt(arr.pop()) - 1))
        yesterday = arr.join("-")

        report.page.add_inner_button(__("Today"), function() {
            frappe.query_report.get_filter('from_date').set_value(frappe.datetime.get_today());
            frappe.query_report.get_filter('to_date').set_value(frappe.datetime.get_today());
        }, "Range");
        report.page.add_inner_button(__("Yesterday"), function() {
            frappe.query_report.get_filter('from_date').set_value(yesterday);
            frappe.query_report.get_filter('to_date').set_value(yesterday);
        }, "Range");
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
			"fieldname": "sales_person",
			"label": __("Sales Person"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Customer Group",
			"default": get_user_default(frappe.session.user),
			"reqd": 1,
		},
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.year_start()
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.year_end()
		},
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		let format_fields = ["net_sales"];

		if (in_list(format_fields, column.fieldname) && data && data[column.fieldname] > 0) {
			value = "<span style='color:green;'>" + value + "</span>";
		}
		return value;
	}
};

function get_user_default(user){
	if(frappe.session.user == 'kuldeepbaddi@gmail.com'){
		return 'All'
	}
}

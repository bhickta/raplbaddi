// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Geyser Production"] = {
	onload: function(report) {
		// arr = frappe.datetime.get_today().split("-")
        // arr.push("0" + (parseInt(arr.pop()) - 1))
        // yesterday = arr.join("-") 

        report.page.add_inner_button(__("Today"), function() {
            frappe.query_report.get_filter('start_date').set_value(frappe.datetime.get_today());
            frappe.query_report.get_filter('end_date').set_value(frappe.datetime.get_today());
        }, "Range");
        // report.page.add_inner_button(__("Yesterday"), function() {
        //     frappe.query_report.get_filter('start_date').set_value(yesterday);
        //     frappe.query_report.get_filter('end_date').set_value(yesterday);
        // }, "Range");
        report.page.add_inner_button(__("Week"), function() {
            frappe.query_report.get_filter('start_date').set_value(frappe.datetime.week_start());
            frappe.query_report.get_filter('end_date').set_value(frappe.datetime.week_end());
        }, "Range");
		report.page.add_inner_button(__("Month"), function() {
			frappe.query_report.get_filter('start_date').set_value(frappe.datetime.month_start());
			frappe.query_report.get_filter('end_date').set_value(frappe.datetime.month_end());
		}, "Range");
		report.page.add_inner_button(__("Quarter"), function() {
			frappe.query_report.get_filter('start_date').set_value(frappe.datetime.quarter_start());
			frappe.query_report.get_filter('end_date').set_value(frappe.datetime.quarter_end());
		}, "Range");
        report.page.add_inner_button(__("Year"), function() {
            frappe.query_report.get_filter('start_date').set_value(frappe.datetime.year_start());
            frappe.query_report.get_filter('end_date').set_value(frappe.datetime.year_end());
        }, "Range");
    },
	"filters": [
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "MultiSelectList",
			width: "80",
			options: "Item Group",
			get_data: function (txt) {
				return frappe.db.get_link_options("Item Group", txt);
			},
			get_query: () => {
			},
		},
		{
			"fieldname": "start_date",
			"label": "Starting Date of Production",
			"fieldtype": "Date",
			"default": frappe.datetime.year_start()
		},
		{
			"fieldname": "end_date",
			"label": "Ending Date of Production",
			"fieldtype": "Date",
			"default": frappe.datetime.year_end()
		},
		// {
		// 	"fieldname": "group_by_item_model_capacity_brand",
		// 	"label": "Group By Item Model Capcity Brand",
		// 	"fieldtype": "Check"
		// },
		// {
		// 	"fieldname": "Test",
		// 	"label": __("Test"),
		// 	"fieldtype": "Button",
		// 	"options": test
		// }
	],
	// test: function(){
	// 	console.log("object");
	// }
};


		// {
		// 	"fieldname":"month",
		// 	"label": __("Month"),
		// 	"fieldtype": "Select",
		// 	"options": " \nJan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec",
		// },

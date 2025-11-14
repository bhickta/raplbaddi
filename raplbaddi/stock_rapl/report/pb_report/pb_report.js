// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["PB Report"] = {
	"filters": [
		{
			"fieldname": "report_type",
			"label": __("Report Type"),
			"fieldtype": "Select",
			"options": "Box Stock\nBox Dispatch\nBox Production\nDead Stock\nUrgent Dispatch",
			"reqd": 1,
			"default": "Box Stock"
		},
		{
			"fieldname": "box_stock",
			"label": __("Box Stock"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "add_priority",
			"label": __("Add Priority"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "over_stock",
			"label": __("Add Over Stock"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "paper_stock",
			"label": __("Add Paper Stock"),
			"fieldtype": "Check"
		},
		{
			"fieldname": "add_links",
			"label": __("Add Links"),
			"fieldtype": "Check"
		}
	],
	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		let format_fields = ["dispatch_need_to_complete_so", "over_stock_qty", "short_qty", "urgent_dispatch"];

		if (in_list(format_fields, column.fieldname) && data && data[column.fieldname] > 0) {
			value = "<span style='color:red;'>" + value + "</span>";
		}
		return value;
	}
};
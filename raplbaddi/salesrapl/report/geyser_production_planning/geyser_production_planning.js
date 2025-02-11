// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["Geyser Production Planning"] = {
	"filters": [
		{
			"fieldname": "report_type",
			"label": __("Report Type"),
			"fieldtype": "Select",
			"options": "Order and Shortage\nItemwise Order and Shortage",
			"reqd": 1,
			"default": "Order and Shortage"
		},
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
	]
};

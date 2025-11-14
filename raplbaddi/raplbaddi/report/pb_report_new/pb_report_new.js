// Copyright (c) 2024, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.query_reports["PB Report New"] = {
	"filters": [
		{
			"fieldname": "report_type",
			"fieldtype": "Select",
			"label": "Report Type",
			"options": "Packing Boxes Stock Report\n",
			"default": "Packing Boxes Stock Report",
			"reqd": 1,
		},
		{
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"label": "Warehouse",
			"filters": {
				"warehouse_type": "Packing Boxes"
			}
		},
		{
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"label": "Item",
			"filters": {
				"item_group": "Packing Boxes"
			},
		},
		{
			"fieldname": "is_group_by",
			"fieldtype": "Check",
			"label": "Group By",
			"default": 0
		},
	]
};

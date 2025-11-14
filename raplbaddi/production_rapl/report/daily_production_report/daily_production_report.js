// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Production Report"] = {
	"filters": [
		{
			"fieldname": "item",
			"label": "Item",
			"fieldtype": "Select",
			"options": "Geyser\nDesert Air Cooler\nElement",
			"default": "Geyser"
		},
		{
			"fieldname": "start_date",
			"label": "Starting Date of Production",
			"fieldtype": "Date",
			"default": dateutil.year_start()
		},
		{
			"fieldname": "end_date",
			"label": "Ending Date of Production",
			"fieldtype": "Date",
			"default": dateutil.year_end()
		},
		{
			"fieldname": "brand_name",
			"label": "Brand Name",
			"fieldtype": "Link",
			"options": "Brand"
		},
		{
			"fieldname": "group_by_brand_model_capacity",
			"label": "Group By Brand, Model and Capacity",
			"fieldtype": "Check"
		},
	]
};

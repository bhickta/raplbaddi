// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Geyser Production Monthly Model and Capacity Wise"] = {
	"filters": [
		{
			"fieldname": "month",
			"label": "Month",
			"fieldtype": "Select",
			"options": "Jan\nFeb\nMar\nApr\nMay\nJun\nJul\nAug\nSep\nOct\nNov\nDec"
		},
		{
			"fieldname": "item",
			"label": "Item",
			"fieldtype": "Select",
			"options": "Geyser\nDesert Cooler\n Element"
		}

	]
};
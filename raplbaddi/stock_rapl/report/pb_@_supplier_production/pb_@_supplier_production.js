// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["PB @ Supplier Production"] = {
	"filters": [
		{
			"fieldname": "supplier",
			"label": "Supplier",
			"fieldtype": "Link",
			"options": "Supplier"
		}
	]
};

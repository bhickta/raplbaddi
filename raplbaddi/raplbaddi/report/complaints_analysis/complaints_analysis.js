// Copyright (c) 2025, Nishant Bhickta and contributors
// For license information, please see license.txt

function get_options() {
	let report_types = ["Complaints Register Per Day", "Pending Complaints Report", "Customer Feedback Report"];
	report_types.push("Days Deadline");
	return report_types.join("\n");
}


frappe.query_reports["Complaints Analysis"] = {
	"filters": [
		{
			"fieldname": "report_type",
			"fieldtype": "Select",
			"label": "Report Type",
			"options": get_options(),
			"reqd": 1
		},
		{
			"fieldname": "is_show_closed",
			"fieldtype": "Check",
			"label": "Show Closed",
			"default": 0,
		},
	]
};

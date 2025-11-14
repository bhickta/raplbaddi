// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt
/* eslint-disable */
get_filters()
function get_filters() {
	frappe.call({
		method: 'raplbaddi.datarapl.doctype.report_full_access_users.report_full_access_users.get_wildcard_users',
		callback: function (r) {
			showFilters = r.message.includes(frappe.session.user)
			if (showFilters) {
				frappe.query_reports["PB at supplier"] = {
					"filters": [
						{
							"fieldname": "supplier",
							"label": __("Supplier"),
							"fieldtype": "Select",
							"width": "160",
							"options": "Jai Ambey Industries\nAmit Print 'N' Pack, Kishanpura, Baddi",
						},
					]
				}
			};
		}
	}
	)
}
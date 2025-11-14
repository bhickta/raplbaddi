// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Requested PB to Production and Receive"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company",
			"reqd": 1,
			"read_only": 1,
			"default": frappe.defaults.get_default("company")
		},
		{
			"fieldname": "supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Supplier",
			"default": get_default_supplier(frappe.session.user),
			"reqd": 1
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
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "material_request",
			"label": __("Material Request"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Material Request",
			"get_query": () => {
				return {
					filters: {
						"docstatus": 1,
						"material_request_type": "Purchase",
						"per_received": ["<", 100]
					}
				}
			}
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item",
			"get_query": () => {
				return {
					filters: {
						"disabled": 0,
						"item_group": "Packing Boxes"
					}
				}
			}
		},
		{
			"fieldname": "group_by_mr",
			"label": __("Group by Material Request"),
			"fieldtype": "Check",
			"default": 0
		},
		{
			"fieldname": "group_by_item",
			"label": __("Group by Item"),
			"fieldtype": "Check",
			"default": 0
		}
	],

	"formatter": function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "ordered_qty" && data && data.ordered_qty > 0) {
			value = "<span style='color:green'>" + value + "</span>";
		}
		return value;
	}
};

function get_default_supplier(user) {
	if(user == 'appdispatch01@gmail.com' || user == 'ppic@amitprintpack.com') {
		return "Amit Print 'N' Pack, Kishanpura, Baddi"
	}else if(user == "production.jaiambey2024@gmail.com"){
		return 'Jai Ambey Industries'
	}
	else{
		return ''
	}
}
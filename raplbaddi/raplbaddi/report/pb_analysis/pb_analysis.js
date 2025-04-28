// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.query_reports["PB Analysis"] = {
    "filters": [
        {
            "fieldname": "item_group",
            "label": "Item Group",
            "fieldtype": "Link",
            "options": "Item Group",
            "reqd": 1,
        },
        {
            "fieldname": "sales_from_date",
            "label": "Sales From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            "reqd": 0
        },
        {
            "fieldname": "sales_to_date",
            "label": "Sales To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 0
        },
        {
            "fieldname": "pr_from_date",
            "label": "PR From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -12),
            "reqd": 0
        },
        {
            "fieldname": "pr_to_date",
            "label": "PR To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 0
        }
    ]
}

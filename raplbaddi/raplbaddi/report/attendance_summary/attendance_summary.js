// Copyright (c) 2024, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.query_reports["Attendance Summary"] = {
    "filters": [
        {
            "fieldname": "report_type",
            "label": __("Report Type"),
            "fieldtype": "Select",
            "options": "Attendance Report\nDetailed Attendance",
            "reqd": 1,
            "default": "Attendance Report"
        },
        {
            "fieldname": "start_date",
            "label": __("Start Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.month_start()
        },
        {
            "fieldname": "end_date",
            "label": __("End Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.month_end()
        },
        {
            "fieldname": "employee",
            "label": __("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "reqd": 0
        },
        {
            "fieldname": "shift_type",
            "label": __("Shift Type"),
            "fieldtype": "Link",
            "options": "Shift Type",
            "reqd": 0
        }
    ]
};
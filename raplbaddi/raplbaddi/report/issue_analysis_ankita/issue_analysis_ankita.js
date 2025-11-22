frappe.query_reports["Issue Analysis Ankita Madaan"] = {
    "filters": [
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nOpen\nClosed\nCancelled",
            "default": "",
            "reqd": 0
        },
        {
            "fieldname": "brand_name",
            "label": __("Brand"),
            "fieldtype": "Link",
            "options": "Brand",
            "default": "",
            "reqd": 0
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        }
    ]
};
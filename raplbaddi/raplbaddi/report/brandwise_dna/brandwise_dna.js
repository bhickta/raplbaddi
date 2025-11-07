// Copyright (c) 2025, Nishant Bhickta and contributors
// For license information, please see license.txt


frappe.query_reports["Brandwise DNA"] = {
    "filters": [
        {
            "fieldname": "brand",
            "label": __("Brand"),
            "fieldtype": "Link",
            "options": "Brand"
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        },
        {
            "fieldname": "item_code",
            "label": __("Item Code"),
            "fieldtype": "Link",
            "options": "Item"
        }
    ]
};

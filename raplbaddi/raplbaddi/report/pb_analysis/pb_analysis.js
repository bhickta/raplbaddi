frappe.query_reports["PB Analysis"] = {
    filters: [
        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group",
            default: "Packing Boxes",
            reqd: 1,
        },
        {
            fieldname: "show_disabled",
            label: __("Show Disabled"),
            fieldtype: "Check",
            default: 0,
        },
        {
            fieldname: "from_date_1",
            label: __("From Date 1"),
            fieldtype: "Date",
            default: frappe.datetime.year_start(),
            reqd: 1,
        },
        {
            fieldname: "to_date_1",
            label: __("To Date 1"),
            fieldtype: "Date",
            default: frappe.datetime.year_end(),
            reqd: 1,
        },
        {
            fieldname: "from_date_2",
            label: __("From Date 2"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.year_start(), -12),
            reqd: 1,
        },
        {
            fieldname: "to_date_2",
            label: __("To Date 2"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.year_end(), -12),
            reqd: 1,
        }
    ],
};

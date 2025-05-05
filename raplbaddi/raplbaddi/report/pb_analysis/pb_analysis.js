frappe.query_reports["PB Analysis"] = {
    filters: [
        {
            fieldname: "item_group",
            label: __("Item Group"),
            fieldtype: "Link",
            options: "Item Group",
            default: "Packing Boxes",
            reqd: 1
        },
        {
            fieldname: "show_disabled",
            label: __("Show Disabled"),
            fieldtype: "Check",
            default: 0
        },
        // ── Previous Financial Year filters now first ──
        {
            fieldname: "from_date_1",
            label: __("From Date 1"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(get_financial_year_start(), -12),
            reqd: 1
        },
        {
            fieldname: "to_date_1",
            label: __("To Date 1"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(get_financial_year_end(), -12),
            reqd: 1
        },
        // ── Current Financial Year filters next ──
        {
            fieldname: "from_date_2",
            label: __("From Date 2"),
            fieldtype: "Date",
            default: get_financial_year_start(),
            reqd: 1
        },
        {
            fieldname: "to_date_2",
            label: __("To Date 2"),
            fieldtype: "Date",
            default: get_financial_year_end(),
            reqd: 1
        }
    ]
};

// Helpers remain unchanged
function get_financial_year_start() {
    let today = frappe.datetime.str_to_obj(frappe.datetime.get_today());
    let year = today.getMonth() + 1 < 4 ? today.getFullYear() - 1 : today.getFullYear();
    return frappe.datetime.obj_to_str(new Date(year, 3, 1));
}
function get_financial_year_end() {
    let today = frappe.datetime.str_to_obj(frappe.datetime.get_today());
    let year = today.getMonth() + 1 < 4 ? today.getFullYear() : today.getFullYear() + 1;
    return frappe.datetime.obj_to_str(new Date(year, 2, 31));
}
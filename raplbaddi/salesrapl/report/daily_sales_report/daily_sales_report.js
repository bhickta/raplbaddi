// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Sales Report"] = {
    onload: function (report) {
        report.page.add_inner_button(__("Today"), function () {
            frappe.query_report.get_filter('start_date').set_value(frappe.datetime.get_today());
            frappe.query_report.get_filter('end_date').set_value(frappe.datetime.get_today());
        }, "Range");
        report.page.add_inner_button(__("Week"), function () {
            frappe.query_report.get_filter('start_date').set_value(frappe.datetime.week_start());
            frappe.query_report.get_filter('end_date').set_value(frappe.datetime.week_end());
        }, "Range");
        report.page.add_inner_button(__("Year"), function () {
            frappe.query_report.get_filter('start_date').set_value(frappe.datetime.year_start());
            frappe.query_report.get_filter('end_date').set_value(frappe.datetime.year_end());
        }, "Range");
        report.page.add_inner_button(__("This Month"), function () {
            frappe.query_report.get_filter('start_date').set_value(frappe.datetime.month_start());
            frappe.query_report.get_filter('end_date').set_value(frappe.datetime.month_end());
        }, "Range");
    },
    "filters": [
        {
            "fieldname": "start_date",
            "label": "Ending Date of Production",
            "fieldtype": "Date",
            "default": frappe.datetime.year_start()
        },
        {
            "fieldname": "end_date",
            "label": "Ending Date of Production",
            "fieldtype": "Date",
            "default": frappe.datetime.year_end()
        },
        {
            "fieldname": "sales_person",
            "label": "Sales Person",
            "fieldtype": "Link",
            "options": "Sales Person",
            "default": frappe.session.user
        },
        {
            "fieldname": "payment_status",
            "label": "Payment Status",
            "fieldtype": "Select",
            "options": "\nUnpaid\nPaid"
        },
        {
            "fieldname": "payment_audited",
            "label": "Payment Audited",
            "fieldtype": "Select",
            "options": "\nYes\nNo",
        },
    ]
};

// var intervalId = window.setInterval(function () {
//     populate_images();
// }, 1000);

// function populate_images() {
//     // This assumes the images go into the first column.
//     $('.dt-cell__content--col-2').map(function (i, el) {
//         var content = $(el).html().trim();
//         if (content.charAt(0) === '/') {
//             $(el).html('<img src="' + content + '"');
//         }
//     });
// }
// Copyright (c) 2024, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.query_reports["Monthly Service Center Payment"] = {
	onload: function (report) {

		report.page.add_inner_button(__("Payment Done"), function () {
			frappe.query_report.get_filter('is_paid').set_value(1);
			frappe.msgprint('Payment Status (Paid),Changed successfully for ' + frappe.query_report.get_filter('service_centre').get_value());
		});
		report.page.add_inner_button(__("Already Paid"), function () {
			frappe.query_report.get_filter('payment_done').set_value("Paid");
			frappe.query_report.get_filter('customer_confirmation').set_value("Positive");
			frappe.query_report.get_filter('service_delivered').set_value("Yes");
			frappe.query_report.get_filter('service_centre').set_value("");
			frappe.query_report.get_filter('group_by_sc').set_value(1);
		});
		report.page.add_inner_button(__("To be Paid"), function () {
			frappe.query_report.get_filter('payment_done').set_value("Unpaid");
			frappe.query_report.get_filter('customer_confirmation').set_value("Positive");
			frappe.query_report.get_filter('service_delivered').set_value("Yes")
			
		});
		report.page.add_inner_button(__("Remove Filters"), function () {
			frappe.query_report.get_filter('payment_done').set_value("");
			frappe.query_report.get_filter('customer_confirmation').set_value("");
			frappe.query_report.get_filter('service_delivered').set_value("");
			frappe.query_report.get_filter('service_centre').set_value("");
			frappe.query_report.get_filter('group_by_sc').set_value(0);
			frappe.query_report.get_filter('is_paid').set_value(0);
			frappe.query_report.get_filter('payment_remarks').set_value("")
		}),
		report.page.add_inner_button(__("Today"), function () {
				frappe.query_report.get_filter('start_date').set_value(frappe.datetime.get_today());
				frappe.query_report.get_filter('end_date').set_value(frappe.datetime.get_today());
			}, "Range");
		report.page.add_inner_button(__("Week"), function () {
			frappe.query_report.get_filter('start_date').set_value(frappe.datetime.week_start());
			frappe.query_report.get_filter('end_date').set_value(frappe.datetime.week_end());
		}, "Range");
		report.page.add_inner_button(__("Month"), function () {
			console.log(typeof (frappe.datetime.month_start()))
			frappe.query_report.get_filter('start_date').set_value(frappe.datetime.month_start());
			frappe.query_report.get_filter('end_date').set_value(frappe.datetime.month_end());
		}, "Range");
		report.page.add_inner_button(__("Quarter"), function () {
			frappe.query_report.get_filter('start_date').set_value(frappe.datetime.quarter_start());
			frappe.query_report.get_filter('end_date').set_value(frappe.datetime.quarter_end());
		}, "Range");
		report.page.add_inner_button(__("Year"), function () {
			frappe.query_report.get_filter('start_date').set_value(frappe.datetime.year_start());
			frappe.query_report.get_filter('end_date').set_value(frappe.datetime.year_end());
		}, "Range");
	},

	"filters": [
		{
			'fieldname': 'service_centre',
			'label': __('Service Centre'),
			'fieldtype': 'Link',
			'options': 'Service Centre'
		},
		{
			'fieldname': 'start_date',
			'label': __('Start Date'),
			'fieldtype': 'Date',
			'reqd': 1
		},
		{
			'fieldname': 'end_date',
			'label': __('End Date'),
			'fieldtype': 'Date',
			'reqd': 1
		},
		{
			'fieldname': 'payment_done',
			'label': __('Payment Status'),
			'fieldtype': 'Select',
			'options': ' \nPaid\nUnpaid'
		},
		{
			'fieldname': 'customer_confirmation',
			'label': __('Customer Feedback'),
			'fieldtype': 'Select',
			'options': '\nNot Taken\nPositive\nNegative',
		},
		{
			'fieldname': 'service_delivered',
			'label': __('Service Delivered'),
			'fieldtype': 'Select',
			'options': ' \nYes\nNo'
		},
		{
			'fieldname': 'group_by_sc',
			'label': __('Group By Service Centre'),
			'fieldtype': 'Check',
			'default': 1
			
		},
		{
			'fieldname': 'is_paid',
			'label': __('Paid to Service Centre'),
			'fieldtype': 'Check',
			'default': 0,
		},
		{
            'fieldname': 'payment_remarks',
            'label': 'Remarks for the payment:',
            'fieldtype': 'Data',
        }
	
	]
};
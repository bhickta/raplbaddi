# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt
from .sub_reports.complaints_register_per_day import ComplaintsRegisterPerDay
from .sub_reports.pending_complaints import PendingComplaintReport
from .sub_reports.pending_complaints_after_deadline import DaysDeadline
from .sub_reports.complaints_feedback_report import CustomerFeedbackReport
from .sub_reports.service_centre_details import ServiceCentreDetailsReport

def get_report_class():
    report_class_map = {
        "Complaints Register Per Day": ComplaintsRegisterPerDay,
        "Pending Complaints Report": PendingComplaintReport,
        "Customer Feedback Report": CustomerFeedbackReport,
        # "Service Centre Details": ServiceCentreDetailsReport,
        # "Days Deadline": DaysDeadline,
    }
    return report_class_map

def execute(filters=None):
    report_type = filters.get("report_type")
    report = get_report_class()[report_type](filters)
    return report.run()

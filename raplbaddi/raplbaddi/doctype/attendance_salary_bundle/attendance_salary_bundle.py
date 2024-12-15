import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
import calendar
from typing import Dict, List

import frappe.utils
import frappe.utils.dateutils


class AttendanceSalaryBundle(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from raplbaddi.raplbaddi.doctype.attendance_salary_bundle_item.attendance_salary_bundle_item import (
            AttendanceSalaryBundleItem,
        )

        amended_from: DF.Link | None
        employee: DF.Link | None
        from_date: DF.Date | None
        items: DF.Table[AttendanceSalaryBundleItem]
        to_date: DF.Date | None
        total_holiday: DF.Float
        total_salary: DF.Float
    # end: auto-generated types

    def validate(self):
        self.validate_items()
        self.validate_salary()
        self.validate_holiday()
    

    def validate_items(self):
        self.add_holidays_item_not_present()
        self.calculate_salary()
    
    def calculate_salary(self):
        for item in self.items:
            salary = Salary(self.employee, item.date)
            item.is_holiday = Holiday.is_holiday(self.employee, item.date)
            if not item.attendance_item:
                default_shift = frappe.get_value("Employee", self.employee, "default_shift")
                shift = frappe.get_doc("Shift Type", default_shift, ["start_time", "end_time"])
                shift_end = shift.end_time
                shift_start = shift.start_time
            else:
                attendance_item = frappe.get_doc("Attendance Rapl Item", item.attendance_item)
                shift_end = attendance_item.end_time
                shift_start = attendance_item.start_time
                item.attendance = attendance_item.attendance
                item.duration = attendance_item.duration

            shift_duration = frappe.utils.time_diff_in_hours(shift_end, shift_start)
            item.hourly_rate = salary.get_hourly_rate(item, shift_duration)
            if item.is_holiday and item.attendance == "Absent" and not item.duration:
                item.duration = frappe.utils.time_diff_in_seconds(shift_end, shift_start)

            item.update(
                {
                    "monthly_salary": salary.get_monthly_salary(item.date),
                    "salary": salary.calculate(item.hourly_rate, item.duration),
                }
            )

    def add_holidays_item_not_present(self):
        missing_dates = self._get_missing_dates()
        self.extend(
            "items",
            [
                {
                    "date": date,
                    "is_holiday": True,
                    "salary": 0.0,
                    "attendance": "Absent",
                }
                for date in missing_dates
                if Holiday.is_holiday(self.employee, date)
            ],
        )

    def _get_missing_dates(self):
        if not self.from_date or not self.to_date:
            frappe.throw("From Date and To Date must be specified.")

        from_date = datetime.strptime(self.from_date, "%Y-%m-%d").date()
        to_date = datetime.strptime(self.to_date, "%Y-%m-%d").date()

        all_dates = {
            from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)
        }

        item_dates = {item.date for item in self.items if item.date}

        missing_dates = all_dates - item_dates
        return missing_dates

    def validate_salary(self):
        self.total_salary = sum(item.salary for item in self.items)

    def validate_holiday(self):
        self.total_holiday = len([item for item in self.items if item.is_holiday])

    def on_trash(self):
        pass


from frappe.utils import getdate


class Salary:
    def __init__(self, employee, year):
        self.monthly_salary = self._get_monthly_salary(employee, year)

    def get_hourly_rate(self, item, shift_duration):
        year, month = item.date.year, item.date.month
        no_of_days = calendar.monthrange(year, item.date.month)[1]
        daily_salary = self.monthly_salary[calendar.month_name[month]] / no_of_days
        hourly_salary = daily_salary / shift_duration
        if item.attendance_item and item.is_holiday and item.attendance == "Absent":
            return hourly_salary
        return hourly_salary * 2 if item.attendance_item and item.is_holiday else hourly_salary

    def calculate(self, hourly_rate: float, duration: float) -> float:
        return hourly_rate * hr(duration)

    def get_monthly_salary(self, date):
        return self.monthly_salary

    def _get_monthly_salary(self, employee, date):
        salary_doc = frappe.get_all(
            "Employee Salary",
            filters={"employee": employee, "year": date.year, "docstatus": 1},
            pluck="name",
        )
        if not salary_doc:
            frappe.throw(f"Please set monthly salary for employee {employee}")
        if len(salary_doc) > 1:
            frappe.throw(f"Please set only one monthly salary for employee {employee}")
        salary_doc = frappe.get_doc("Employee Salary", salary_doc[0])
        return {item.month: item.value for item in salary_doc.items}


def hr(seconds: int) -> float:
    return seconds / 3600


class Holiday:

    @staticmethod
    def is_holiday(employee, date):
        holiday_list = Holiday.get_list(employee)
        return date in holiday_list

    @staticmethod
    def get_list(employee) -> Dict:
        holiday_list, company, default_shift = frappe.get_cached_value(
            "Employee", employee, ["holiday_list", "company", "default_shift"]
        )
        if not holiday_list and default_shift:
            holiday_list = frappe.get_cached_value(
                "Shift Type", default_shift, "holiday_list"
            )
        if not holiday_list:
            holiday_list = frappe.get_cached_value(
                "Company", company, "default_holiday_list"
            )
        if not holiday_list:
            frappe.throw(
                f"Please set a default Holiday List for Employee {employee} or Company {company}"
            )
        return {
            holiday["holiday_date"]: holiday["description"]
            for holiday in frappe.get_all(
                "Holiday",
                filters={"parent": holiday_list},
                fields=["holiday_date", "description"],
            )
        }


class Attendance:

    @staticmethod
    def get_attendances(employee, from_date, to_date) -> List[str]:
        return frappe.get_all(
            "Attendance Rapl Item",
            filters={
                "date": ["between", (from_date, to_date)],
                "docstatus": 1,
                "employee": employee,
            },
            pluck="name",
        )

    @staticmethod
    def get_duration(employee, shift_type, duration) -> float:
        if not shift_type:
            shift_type = frappe.get_value("Employee", employee, "default_shift")

        start_time, end_time, time_allowance = frappe.get_cached_value(
            "Shift Type",
            shift_type,
            ["start_time", "end_time", "time_allowance"],
        )
        shift_duration = (end_time - start_time).total_seconds()
        if not duration:
            duration = shift_duration
        return (
            hr(shift_duration)
            if abs(duration - time_allowance) < shift_duration
            else hr(duration)
        )
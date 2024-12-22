import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
import calendar
from typing import Dict, List

import frappe.utils
from frappe.utils import dateutils

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
        self.validate_total()
    
    def validate_items(self):
        self.set_day_of_the_week()
        self.add_holidays_item_not_present()
        self.validate_holiday()
        self.validate_holiday_sandwich()
        self.preitem()
        self.calcualte_salary()
    
    def set_day_of_the_week(self):
        for item in self.items:
            item.day = calendar.day_name[item.date.weekday()]
    
    def validate_holiday(self):
        for item in self.items:
            item.is_holiday = Holiday.is_holiday(self.employee, item.date)

    def validate_holiday_sandwich(self):
        for item in self.items:
            if item.is_holiday and item.day in ["Sunday",]:
                print(item.date)
                item.is_holiday_sandwich = Holiday.is_holiday_sandwich(self.employee, item.date)
                print(item.is_holiday_sandwich)
            if item.is_holiday_sandwich:
                item.is_holiday = False

    def preitem(self):
        for item in self.items:
            salary = Salary(self.employee, item.date)
            if not item.attendance_item:
                self.set_default_values(item)
            else:
                self.set_values_from_attendance_item(item)

            shift_duration = frappe.utils.time_diff_in_hours(item.shift_end, item.shift_start)
            item.hourly_rate = salary.get_hourly_rate(item, shift_duration)
            if item.is_holiday and item.attendance == "Absent" and not item.duration:
                item.duration = frappe.utils.time_diff_in_seconds(item.shift_end, item.shift_start)

            item.monthly_salary = salary.get_monthly_salary(item.date)
    
    def set_default_values(self, item):
        default_shift = frappe.get_value("Employee", self.employee, "default_shift")
        shift = frappe.get_doc("Shift Type", default_shift, ["start_time", "end_time"])
        item.shift_end = shift.end_time
        item.shift_start = shift.start_time
    
    def set_values_from_attendance_item(self, item):
        attendance_item = frappe.get_doc("Attendance Rapl Item", item.attendance_item)
        item.shift_end = attendance_item.end_time
        item.shift_start = attendance_item.start_time
        item.attendance = attendance_item.attendance
        item.duration = attendance_item.duration

    def calcualte_salary(self):
        for item in self.items:
            item.salary = item.hourly_rate * hr(item.duration)

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

    def validate_total(self):
        self.total_salary = sum(item.salary for item in self.items)
        self.total_holiday = len([item for item in self.items if item.is_holiday])

    def on_trash(self):
        pass

from frappe.utils import getdate


class Salary:
    def __init__(self, employee, year):
        self.monthly_salary = self._get_monthly_salary(employee, year)

    def get_hourly_rate(self, item, shift_duration):
        year, month = item.date.year, item.date.month
        shift_duration -= 0.5
        no_of_days = calendar.monthrange(year, item.date.month)[1]
        daily_salary = self.monthly_salary[calendar.month_name[month]] / no_of_days
        hourly_salary = daily_salary / shift_duration
        if item.attendance_item and item.is_holiday and item.attendance == "Absent":
            return hourly_salary
        double_rate = self.is_double_rate(item)
        if shift_duration and double_rate and item.duration > shift_duration:
            item.duration = shift_duration * 3600
        return hourly_salary * 2 if double_rate else hourly_salary

    def is_double_rate(self, item):
        return self.present_on_holidays(item)
    
    def present_on_holidays(self, item):
        return item.is_holiday and item.attendance == "Present"
        
    def get_monthly_salary(self, date):
        return self.monthly_salary[calendar.month_name[date.month]]

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
    def is_holiday(employee: str, date):
        holiday_list = Holiday.get_list(employee)
        return date in holiday_list

    @staticmethod
    def is_holiday_sandwich(employee, date):
        employee = frappe.get_doc("Employee", employee, ["department"])
        ret = False
        if not employee.department:
            return ret
        holiday_sandwich = frappe.get_all("Holiday Sandwich", {"department": employee.department}, ['minimum_weekly_attendance'])
        if not holiday_sandwich:
            return ret
        minimum_weekly_attendance = holiday_sandwich[0].minimum_weekly_attendance
        weekly_attendance = Holiday.weekly_attendance(employee, date)
        if weekly_attendance < minimum_weekly_attendance:
            ret = True

        return ret
    
    @staticmethod
    def weekly_attendance(employee, date):
        week_start = dateutils.get_first_day_of_week(date)
        week_end = dateutils.get_last_day_of_week(date)
        attendance = frappe.get_all("Attendance Rapl Item", filters={"employee": employee.name, "docstatus": 1, "date": ["between", [week_start, week_end]]})
        if not attendance:
            return 0
        return len(attendance)

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
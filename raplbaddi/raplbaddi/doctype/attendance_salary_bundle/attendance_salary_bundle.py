import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta
import calendar
from typing import Dict, List
import math

import frappe.utils
from raplbaddi.utils import dateutils

lunch_start = "13:00:00"
lunch_end = "13:30:00"
lunch_duration_sec = frappe.utils.time_diff_in_seconds(lunch_end, lunch_start)
lunch_duration_hour = frappe.utils.time_diff_in_hours(lunch_end, lunch_start)


class AttendanceSalaryBundle(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from raplbaddi.raplbaddi.doctype.attendance_salary_bundle_item.attendance_salary_bundle_item import AttendanceSalaryBundleItem

        amended_from: DF.Link | None
        employee: DF.Link | None
        exact_salary: DF.Float
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
        self.calculate_salary()
        self.order_item_based_on_date()


    def set_day_of_the_week(self):
        for item in self.items:
            if isinstance(item.date, str):
                item.date = datetime.strptime(item.date, "%Y-%m-%d").date()
            item.day = calendar.day_name[item.date.weekday()]

    def validate_holiday(self):
        for item in self.items:
            item.is_holiday = Holiday.is_holiday(self.employee, item.date)

    def validate_holiday_sandwich(self):
        for item in self.items:
            if item.is_holiday and item.day in [
                "Sunday",
            ]:
                item.is_holiday_sandwich = Holiday.is_holiday_sandwich(
                    self.employee, item.date
                )
            if item.is_holiday_sandwich:
                item.is_holiday = False

    def preitem(self):
        for item in self.items:
            salary = Salary(self.employee, item.date)
            if not item.attendance_item:
                self.set_default_values(item)
            else:
                self.set_values_from_attendance_item(item)

            item.hourly_rate = salary.get_hourly_rate(item)
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
        item.duration, item.shift_duration = Attendance.get_durations(self.employee, attendance_item)

    def calculate_salary(self):
        for item in self.items:
            shift_duration = hr(item.shift_duration)
            duration = hr(item.duration)
            item.salary = 0
            item.calculation = ""  # Initialize calculation field

            if item.is_holiday:
                if item.attendance == "Present":
                    if shift_duration >= duration >= 8:
                        item.salary = item.hourly_rate * shift_duration
                        item.calculation = f"{item.hourly_rate:.2f} * {shift_duration:.2f} = {item.salary:.2f}"
                    else:
                        overtime = 2 * item.hourly_rate * min(duration, shift_duration)
                        extra_hours = item.hourly_rate * abs(shift_duration - duration)
                        item.salary = overtime + extra_hours
                        item.calculation = (
                            f"2 * {item.hourly_rate:.2f} * min({duration:.2f}, {shift_duration:.2f}) "
                            f"+ {item.hourly_rate:.2f} * abs({shift_duration:.2f} - {duration:.2f}) = {item.salary:.2f}"
                        )
                elif item.attendance == "Absent":
                    item.salary = shift_duration * item.hourly_rate
                    item.calculation = f"{shift_duration:.2f} * {item.hourly_rate:.2f} = {item.salary:.2f}"
            else:
                item.salary = item.hourly_rate * duration
                item.calculation = f"{item.hourly_rate:.2f} * {duration:.2f} = {item.salary:.2f}"

    def add_holidays_item_not_present(self):
        missing_dates = self._get_missing_dates()
        self.extend(
            "items",
            [
                {
                    "date": date,
                    "is_holiday": True,
                    "day": calendar.day_name[date.weekday()],
                    "salary": 0.0,
                    "attendance": "Absent",
                }
                for date in missing_dates
                if Holiday.is_holiday(self.employee, date)
            ],
        )

    def order_item_based_on_date(self):
        self.items = sorted(self.items, key=lambda item: item.date)
        for new_idx, item in enumerate(self.items, start=1):
            item.idx = new_idx

    def _get_missing_dates(self):
        if not self.from_date or not self.to_date:
            frappe.throw("From Date and To Date must be specified.")
        from_date = datetime.strptime(self.from_date, "%Y-%m-%d").date() if isinstance(self.from_date, str) else self.from_date
        to_date = datetime.strptime(self.to_date, "%Y-%m-%d").date() if isinstance(self.to_date, str) else self.to_date

        all_dates = {
            from_date + timedelta(days=i) for i in range((to_date - from_date).days + 1)
        }

        item_dates = {item.date for item in self.items if item.date}

        missing_dates = all_dates - item_dates
        return missing_dates

    def validate_total(self):
        self.exact_salary = sum(item.salary for item in self.items)
        self.total_holiday = len([item for item in self.items if item.is_holiday])
        self.total_salary = round(self.exact_salary, -2)

    def on_trash(self):
        pass


class Salary:
    def __init__(self, employee, year):
        self.monthly_salary = self._get_monthly_salary(employee, year)

    def get_hourly_rate(self, item):
        year, month = item.date.year, item.date.month
        no_of_days = calendar.monthrange(year, item.date.month)[1]
        daily_salary = self.monthly_salary[calendar.month_name[month]] / no_of_days
        hourly_salary = daily_salary / (item.shift_duration/3600)
        return hourly_salary

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
    if not seconds:
        return 0
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
        holiday_sandwich = frappe.get_all(
            "Holiday Sandwich",
            {"department": employee.department},
            ["minimum_weekly_attendance"],
        )
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
        attendance = frappe.get_all(
            "Attendance Rapl Item",
            filters={
                "employee": employee.name,
                "docstatus": 1,
                "date": ["between", [week_start, week_end]],
                "attendance": "Present",
            },
        )
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
    def get_durations(employee, attendance_item) -> tuple[float, float]:
        if not attendance_item.shift_type:
            attendance_item.shift_type = frappe.get_value(
                "Employee", employee, "default_shift"
            )

        start_time, end_time, time_allowance = frappe.get_cached_value(
            "Shift Type",
            attendance_item.shift_type,
            ["start_time", "end_time", "time_allowance"],
        )
        shift_duration = (end_time - start_time).total_seconds()
        shift_duration_timedelta = timedelta(seconds=shift_duration)
        half_shift_duration = timedelta(seconds=shift_duration / 2)
        shift_duration -= lunch_duration_sec
        global lunch_start
        if attendance_item.duration == 0:
            return (0, shift_duration)

        if isinstance(lunch_start, str):
            hours, minutes, seconds = map(int, lunch_start.split(":"))
            lunch_start = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        if isinstance(attendance_item.check_out, str):
            hours, minutes, seconds = map(int, attendance_item.check_out.split(":"))
            attendance_item.check_out = timedelta(
                hours=hours, minutes=minutes, seconds=seconds
            )

        if lunch_start <= attendance_item.check_out < half_shift_duration:
            attendance_item.duration = shift_duration / 2

        return (
            (attendance_item.duration, shift_duration)
            if abs(attendance_item.duration - shift_duration)
            > time_allowance
            else (shift_duration, shift_duration)
        )
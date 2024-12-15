import frappe
from frappe.model.document import Document
from typing import List, Dict
import calendar
from datetime import datetime

class SalarySlipsRapl(Document):

    def autoname(self):
        self.naming_series = "SSR-.YY.-.#"

    def validate(self):
        for item in self.items:
            attendance_salary_bundle = AttendanceSalaryBundleHandler.create_or_update(item, self.from_date, self.to_date)
            self.ensure_not_duplicate(item.employee, self.from_date, self.to_date)
            item.attendance_salary_bundle = attendance_salary_bundle.name
            item.salary = attendance_salary_bundle.total_salary
            item.holidays = attendance_salary_bundle.total_holiday

    def ensure_not_duplicate(employee, from_date, to_date):
        asbi = frappe.db.sql(
            """
                SELECT asb.name
                FROM `tabAttendance Salary Bundle Item` asbi
                JOIN `tabAttendance Salary Bundle` asb ON asb.name = asbi.parent
                WHERE asb.employee = %s
                AND asbi.date BETWEEN %s AND %s
                AND asb.docstatus = 1
            """, (employee, from_date, to_date))
        if asbi:
            frappe.throw(f"Salary is already created for the employee {employee} between {from_date} and {to_date} </br>" + "</br>".join([item[0] for item in asbi]))

    def on_submit(self):
        AttendanceSalaryBundleHandler.submit_all(self.items)

    def on_cancel(self):
        AttendanceSalaryBundleHandler.cancel_all(self.items)

    def on_trash(self):
        AttendanceSalaryBundleHandler.delete_all(self.items)

class AttendanceSalaryBundleHandler:

    @staticmethod
    def create_or_update(item, from_date, to_date):
        attendances = AttendanceFetcher.get_attendances(item.employee, from_date, to_date)
        attendance_salary_bundle = frappe.get_doc("Attendance Salary Bundle", item.attendance_salary_bundle) if item.attendance_salary_bundle else frappe.new_doc("Attendance Salary Bundle")
        attendance_salary_bundle.employee = item.employee
        attendance_salary_bundle.items = []

        for attendance_name in attendances:
            attendance = frappe.get_doc("Attendance Rapl Item", attendance_name)
            bundle_item = AttendanceSalaryBundleHandler.create_bundle_item(attendance)
            attendance_salary_bundle.append("items", bundle_item)

        attendance_salary_bundle.total_salary = sum(item.salary for item in attendance_salary_bundle.items)
        attendance_salary_bundle.total_holiday = sum(int(item.is_holiday) for item in attendance_salary_bundle.items)
        attendance_salary_bundle.save()
        return attendance_salary_bundle

    @staticmethod
    def create_bundle_item(attendance):
        is_holiday = Holiday.is_holiday(attendance.employee, attendance.date)
        shift_duration = ShiftCalculator.get_duration(attendance)
        hourly_rate = SalaryCalculator.get_hourly_rate(attendance.employee, attendance.date, is_holiday, shift_duration)

        return {
            "attendance_rapl": attendance.parent,
            "attendance_item": attendance.name,
            "duration": attendance.duration,
            "date": attendance.date,
            "hourly_rate": hourly_rate,
            "monthly_salary": MonthlySalaryFetcher.get_monthly(attendance.employee, attendance.date.year)[attendance.date.strftime("%B")],
            "salary": SalaryCalculator.calculate(hourly_rate, attendance.duration),
            "is_holiday": is_holiday,
            "shift_duration": shift_duration * 3600
        }

    @staticmethod
    def submit_all(items):
        for item in items:
            attendance_salary_bundle = frappe.get_doc("Attendance Salary Bundle", item.attendance_salary_bundle)
            attendance_salary_bundle.submit()
    @staticmethod
    def cancel_all(items):
        for item in items:
            attendance_salary_bundle = frappe.get_doc("Attendance Salary Bundle", item.attendance_salary_bundle)
            for bundle_item in attendance_salary_bundle.items:
                bundle_item.attendance = None
                bundle_item.attendance_item = None
            attendance_salary_bundle.save()
            attendance_salary_bundle.cancel()
            item.attendance_salary_bundle = None
    @staticmethod
    def delete_all(items):
        for item in items:
            frappe.delete_doc("Attendance Salary Bundle", item.attendance_salary_bundle)


class AttendanceFetcher:

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

class Holiday:

    @staticmethod
    def is_holiday(employee, date):
        holiday_list = Holiday.get_list(employee)
        return date in holiday_list

    @staticmethod
    def get_list(employee) -> Dict:
        holiday_list, company, default_shift = frappe.get_cached_value("Employee", employee, ["holiday_list", "company", "default_shift"])
        if not holiday_list and default_shift:
            holiday_list = frappe.get_cached_value("Shift Type", default_shift, "holiday_list")
        if not holiday_list:
            holiday_list = frappe.get_cached_value("Company", company, "default_holiday_list")
        if not holiday_list:
            frappe.throw(f"Please set a default Holiday List for Employee {employee} or Company {company}")
        return {
            holiday["holiday_date"]: holiday["description"]
            for holiday in frappe.get_all("Holiday", filters={"parent": holiday_list}, fields=["holiday_date", "description"])
        }

class ShiftCalculator:

    @staticmethod
    def get_duration(attendance) -> float:
        start_time, end_time, time_allowance = frappe.get_cached_value("Shift Type", attendance.shift_type, ["start_time", "end_time", "time_allowance"])
        shift_duration = (end_time - start_time).total_seconds()
        return hr(shift_duration) if abs(attendance.duration - time_allowance) < shift_duration else hr(attendance.duration)

class SalaryCalculator:

    @staticmethod
    def get_hourly_rate(employee, date, is_holiday, shift_duration):
        year, month = date.year, date.strftime("%B")
        monthly_salary = MonthlySalaryFetcher.get_monthly(employee, year)
        no_of_days = calendar.monthrange(year, date.month)[1]
        daily_salary = monthly_salary[month] / no_of_days
        hourly_salary = daily_salary / shift_duration
        return hourly_salary * 2 if is_holiday else hourly_salary

    @staticmethod
    def calculate(hourly_rate: float, duration: float) -> float:
        return hourly_rate * hr(duration)

class MonthlySalaryFetcher:

    @staticmethod
    def get_monthly(employee, year):
        salary_doc = frappe.get_all("Employee Salary", filters={"employee": employee, "year": year, "docstatus": 1}, pluck="name")
        if not salary_doc:
            frappe.throw(f"Please set monthly salary for employee {employee}")
        if len(salary_doc) > 1:
            frappe.throw(f"Please set only one monthly salary for employee {employee}")
        salary_doc = frappe.get_doc("Employee Salary", salary_doc[0])
        return {item.month: item.value for item in salary_doc.items}


def hr(seconds: int) -> float:
    return seconds / 3600
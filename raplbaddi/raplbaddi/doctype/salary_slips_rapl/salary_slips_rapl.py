# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from typing import TYPE_CHECKING, List, Dict
import calendar
from datetime import datetime


class SalarySlipsRapl(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from raplbaddi.raplbaddi.doctype.salary_slips_rapl_item.salary_slips_rapl_item import SalarySlipsRaplItem

        amended_from: DF.Link | None
        branch: DF.Link | None
        department: DF.Link | None
        from_date: DF.Date
        items: DF.Table[SalarySlipsRaplItem]
        naming_series: DF.Literal[None]
        to_date: DF.Date
    # end: auto-generated types

    def validate(self):
        for item in self.items:
            attendance_salary_bundle = self.create_attendance_salary_bundle(item)
            is_salary_created_for_employee(item.employee, self.from_date, self.to_date)
            item.attendance_salary_bundle = attendance_salary_bundle.name
            item.salary = attendance_salary_bundle.total_salary
            item.holidays = attendance_salary_bundle.total_holiday
    
    def autoname(self):
        self.naming_series = "SSR-.YY.-.#"

    def on_submit(self):
        self.submit_salary_bundles()

    def on_cancel(self):
        self.cancel_salary_bundles()

    def on_trash(self):
        self.delete_salary_bundles()

    def after_delete(self):
        for item in self.items:
            frappe.delete_doc("Attendance Salary Bundle", item.attendance_salary_bundle)

    def get_attendances(self, employee: str) -> List[str]:
        return frappe.get_all(
            "Attendance Rapl Item",
            filters={
                "date": ["between", (self.from_date, self.to_date)],
                "docstatus": 1,
                "employee": employee,
            },
            pluck="name",
        )

    def create_attendance_salary_bundle(self, item):
        attendances = self.get_attendances(item.employee)
        attendance_salary_bundle = (
            frappe.get_doc("Attendance Salary Bundle", item.attendance_salary_bundle)
            if item.attendance_salary_bundle
            else frappe.new_doc("Attendance Salary Bundle")
        )

        attendance_salary_bundle.employee = item.employee
        attendance_salary_bundle.items = []

        for attendance_name in attendances:
            attendance = frappe.get_doc("Attendance Rapl Item", attendance_name)
            bundle_item = {
                "attendance_rapl": attendance.parent,
                "attendance_item": attendance.name,
                "duration": attendance.duration,
                "date": attendance.date,
            }
            bundle_item.update(self.get_salary_for_attendance(attendance))
            attendance_salary_bundle.append("items", bundle_item)

        attendance_salary_bundle.total_salary = sum(
            item.salary for item in attendance_salary_bundle.items
        )
        attendance_salary_bundle.total_holiday = sum(
            int(item.is_holiday) for item in attendance_salary_bundle.items
        )
        attendance_salary_bundle.save()
        return attendance_salary_bundle

    def get_salary_for_attendance(self, attendance):
        is_holiday = is_holiday_for_employee(attendance.employee, attendance.date)
        shift_duration = get_shift_duration(attendance)
        hourly_rate = get_hourly_rate(
            attendance.employee, attendance.date, is_holiday, shift_duration
        )

        salary = self.calculate_salary(hourly_rate, attendance.duration)
        return {
            "hourly_rate": hourly_rate,
            "monthly_salary": get_monthly_salary_dict_employee(
                attendance.employee, attendance.date.year
            )[attendance.date.strftime("%B")],
            "date": attendance.date,
            "salary": salary,
            "duration": attendance.duration,
            "attendance": attendance.attendance,
            "is_holiday": is_holiday,
            "shift_duration": shift_duration * 3600,
        }

    @staticmethod
    def calculate_salary(hourly_rate: float, duration: float) -> float:
        return hourly_rate * hr(duration)

    def submit_salary_bundles(self):
        for item in self.items:
            attendance_salary_bundle = frappe.get_doc(
                "Attendance Salary Bundle", item.attendance_salary_bundle
            )
            attendance_salary_bundle.submit()

    def cancel_salary_bundles(self):
        for item in self.items:
            attendance_salary_bundle = frappe.get_doc(
                "Attendance Salary Bundle", item.attendance_salary_bundle
            )
            for item in attendance_salary_bundle.items:
                item.attendance = None
                item.attendance_item = None
            attendance_salary_bundle.save()
            attendance_salary_bundle.cancel()
            item.attendance_salary_bundle = None

    def delete_salary_bundles(self):
        pass


def hr(seconds: int) -> float:
    return seconds / 3600


def get_monthly_salary_dict_employee(employee: str, year: int) -> List[Dict]:
    salary_doc = frappe.get_all("Employee Salary", filters={"employee": employee, "year": year, "docstatus": 1}, pluck="name")
    if not salary_doc:
        frappe.throw(f"Please set monthly salary for employee {employee}")
    if len(salary_doc) > 1:
        frappe.throw(f"Please set only one monthly salary for employee {employee}")
    salary_doc = frappe.get_doc("Employee Salary", salary_doc[0])
    monthly_salary_dict = {
        item.month: item.value
        for item in salary_doc.items
    }
    return monthly_salary_dict


def get_hourly_rate(
    employee: str, date: str, is_holiday: bool, shift_duration: float
) -> float:
    year, month = date.year, date.strftime("%B")
    monthly_salary = get_monthly_salary_dict_employee(employee, year)
    if not monthly_salary:
        frappe.throw(f"Please set monthly salary for employee {employee}")
    no_of_days = calendar.monthrange(year, date.month)[1]
    daily_salary = monthly_salary[month] / no_of_days
    hourly_salary = daily_salary / shift_duration

    return hourly_salary * 2 if is_holiday else hourly_salary


def get_shift_duration(attendance) -> float:
    start_time, end_time, time_allowance = frappe.get_cached_value(
        "Shift Type",
        attendance.shift_type,
        ["start_time", "end_time", "time_allowance"],
    )

    shift_duration = (end_time - start_time).total_seconds()
    return (
        hr(shift_duration)
        if abs(attendance.duration - time_allowance) < shift_duration
        else hr(attendance.duration)
    )


def get_holiday_list_for_employee(employee: str, raise_exception: bool = True) -> Dict:
    if employee:
        holiday_list, company, default_shift = frappe.get_cached_value(
            "Employee", employee, ["holiday_list", "company", "default_shift"]
        )
        if not holiday_list and default_shift:
            holiday_list = frappe.get_cached_value(
                "Shift Type", default_shift, "holiday_list"
            )
    else:
        holiday_list = ""
        company = frappe.db.get_single_value("Global Defaults", "default_company")

    if not holiday_list:
        holiday_list = frappe.get_cached_value(
            "Company", company, "default_holiday_list"
        )

    if not holiday_list and raise_exception:
        frappe.throw(
            f"Please set a default Holiday List for Employee {employee} or Company {company}"
        )

    holidays = frappe.get_all(
        "Holiday",
        filters={"parent": holiday_list},
        fields=["holiday_date", "description"],
    )
    return {holiday["holiday_date"]: holiday["description"] for holiday in holidays}


def is_holiday_for_employee(employee: str, date):
    holiday_list = get_holiday_list_for_employee(employee)
    return date in holiday_list


def is_salary_created_for_employee(employee, from_date, to_date):
    asbi = frappe.db.sql(
        f"""
            SELECT asb.name
            FROM `tabAttendance Salary Bundle Item` asbi
            JOIN `tabAttendance Salary Bundle` asb ON asb.name = asbi.parent
            WHERE asb.employee = '{employee}'
            AND asbi.date between '{from_date}' and '{to_date}'
            AND asb.docstatus = 1"""
    )
    if asbi:
        frappe.throw(f"Salary is already created for the employee {employee} between {from_date} and {to_date} </br>" + "</br>".join([item[0] for item in asbi]))
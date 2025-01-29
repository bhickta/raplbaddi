import frappe
from frappe.model.document import Document
from typing import List
from raplbaddi.raplbaddi.doctype.attendance_salary_bundle.attendance_salary_bundle import (
    Attendance,
)
from datetime import datetime, timedelta


class SalarySlipsRapl(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from raplbaddi.raplbaddi.doctype.salary_slips_rapl_item.salary_slips_rapl_item import (
            SalarySlipsRaplItem,
        )

        amended_from: DF.Link | None
        branch: DF.Link | None
        department: DF.Link | None
        employee: DF.Link | None
        from_date: DF.Date
        items: DF.Table[SalarySlipsRaplItem]
        naming_series: DF.Literal[None]
        status: DF.Literal["", "Audited"]
        to_date: DF.Date
    # end: auto-generated types
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.in_delete = False

    def autoname(self):
        self.naming_series = "SSR-.YY.-.#"

    def validate(self):
        if not self.in_delete:
            self.validate_items()

    def validate_items(self):
        for item in self.items:
            attendance_salary_bundle = AttendanceSalaryBundleHandler.create_or_update(
                item, self.from_date, self.to_date
            )
            self.ensure_not_duplicate(item.employee, self.from_date, self.to_date)
            item.attendance_salary_bundle = attendance_salary_bundle.name
            item.salary = attendance_salary_bundle.total_salary
            item.holidays = attendance_salary_bundle.total_holiday

    def ensure_not_duplicate(self, employee, from_date, to_date):
        asbi = frappe.db.sql(
            """
                SELECT asb.name
                FROM `tabAttendance Salary Bundle Item` asbi
                JOIN `tabAttendance Salary Bundle` asb ON asb.name = asbi.parent
                WHERE asb.employee = %s
                AND asbi.date BETWEEN %s AND %s
                AND asb.docstatus = 1
            """,
            (employee, from_date, to_date),
        )
        if asbi:
            frappe.throw(
                f"Salary is already created for the employee {employee} between {from_date} and {to_date} </br>"
                + "</br>".join([item[0] for item in asbi])
            )

    def before_submit(self):
        if self._action == "cancel":
            return
        mandatory = [
            {
                "status": "Audited",
            }
        ]
        for item in mandatory:
            for field, value in item.items():
                if not self.get(field) == value:
                    frappe.throw(f"{field.capitalize()} must be {value}")

    def on_submit(self):
        AttendanceSalaryBundleHandler.submit_all(self.items)

    def on_cancel(self):
        AttendanceSalaryBundleHandler.cancel_all(self.items)

    def on_trash(self):
        AttendanceSalaryBundleHandler.delete_all(self)


class AttendanceSalaryBundleHandler:

    @staticmethod
    def create_or_update(item, from_date, to_date):
        attendances = Attendance.get_attendances(item.employee, from_date, to_date)
        attendance_salary_bundle = (
            frappe.get_doc("Attendance Salary Bundle", item.attendance_salary_bundle)
            if item.attendance_salary_bundle
            else frappe.new_doc("Attendance Salary Bundle")
        )
        attendance_salary_bundle.employee = item.employee
        attendance_salary_bundle.items = []

        for attendance_name in attendances:
            attendance = frappe.get_doc("Attendance Rapl Item", attendance_name)
            bundle_item = AttendanceSalaryBundleHandler.create_bundle_item(attendance)
            attendance_salary_bundle.append("items", bundle_item)
        attendance_salary_bundle.from_date = from_date
        attendance_salary_bundle.to_date = to_date

        attendance_salary_bundle.save()
        return attendance_salary_bundle

    @staticmethod
    def create_bundle_item(attendance):
        item = frappe._dict(
            {
                "attendance_rapl": attendance.parent,
                "shift_type": attendance.shift_type,
                "attendance_item": attendance.name,
                "duration": attendance.duration,
                "date": attendance.date,
            }
        )
        return item

    @staticmethod
    def submit_all(items):
        for item in items:
            attendance_salary_bundle = frappe.get_doc(
                "Attendance Salary Bundle", item.attendance_salary_bundle
            )
            attendance_salary_bundle.submit()

    @staticmethod
    def cancel_all(items):
        for item in items:
            attendance_salary_bundle = frappe.get_doc(
                "Attendance Salary Bundle", item.attendance_salary_bundle
            )
            for bundle_item in attendance_salary_bundle.items:
                bundle_item.attendance_item = None
            attendance_salary_bundle.save()
            attendance_salary_bundle.cancel()
            item.attendance_salary_bundle = None

    @staticmethod
    def delete_all(doc):
        bundles = [item.attendance_salary_bundle for item in doc.items]
        for item in doc.items:
            item.attendance_salary_bundle = None
        doc.in_delete = True
        doc.save()
        for bundle in bundles:
            frappe.delete_doc("Attendance Salary Bundle", bundle)

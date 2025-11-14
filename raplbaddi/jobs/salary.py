import frappe
from frappe.utils.dateutils import getdate, add_to_date
prefix = 'salary'
from datetime import datetime


def yearly():
    employee_salary = frappe.get_all('Employee Salary', ['name', 'employee'], filters={'docstatus': 1}, as_list=True)

    for salary, employee in employee_salary:
        employee_status = frappe.db.get_value('Employee', employee, 'status')
        if employee_status not in ('Active',):
            continue
        current_year = getdate().year
        salary_doc = frappe.get_doc('Employee Salary', salary)
        new_year_salary_doc = frappe.copy_doc(salary_doc)
        new_year_salary_doc.year = current_year
        for item in new_year_salary_doc.items:
            item.year = current_year
            item.value = salary_doc.get('items')[-1].get('value')
        try:
            new_year_salary_doc.save()
            new_year_salary_doc.submit()
        except frappe.DuplicateEntryError:
            pass
        
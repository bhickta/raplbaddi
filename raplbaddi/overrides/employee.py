import frappe


def autoname(doc, method):
    doc.employee, doc.name = None, None
    if not doc.department or doc.branch == None:
        frappe.throw("Department and branch is Mandatory")
    if doc.branch == "RAPL Unit-1":
        naming_for_branch_rapl_unit_one(doc)
    elif doc.branch == "Red Star Unit 2":
        naming_for_branch_red_star_unit_two(doc, method)

def naming_for_branch_red_star_unit_two(doc, method):
    if doc.custom_employee_code:
        doc.name = doc.custom_employee_code
    else:
        naming_for_branch_rapl_unit_one(doc, "RSI", 40)

def naming_for_branch_rapl_unit_one(doc, suffix="E", upper_limit=30):
    filters = {"branch": doc.branch, "naming_series": ["like", f"{suffix}-%"]}
    if len(frappe.get_all("Employee", filters=filters)) == 0:
        middle_no = 1
    else:
        last_employee = frappe.get_last_doc("Employee", filters=filters).name.split("-")

        middle_no = get_middle_no(last_employee[1])
        if int(last_employee[2]) == upper_limit:
            middle_no += 1
    doc.naming_series = f"{suffix}-{get_middle_no(middle_no)}-.#"

def get_middle_no(value):
    if isinstance(value, int):
        if value < 1:
            raise ValueError("Input must be a positive integer.")
        
        result = ""
        
        while value > 0:
            value -= 1
            result = chr(value % 26 + ord('A')) + result
            value //= 26
        
        return result
    
    elif isinstance(value, str):
        result = 0
        for char in value:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result
    else:
        raise ValueError("Input must be an integer or a string.")

def validate(doc, method):
    set_account_holder_name(doc)
    validate_mandatory(doc)
    set_salary(doc)

def validate_mandatory(doc):
    if not doc.ctc:
        frappe.throw("CTC is mandatory")

import calendar
from frappe.utils.data import now_datetime
def set_salary(doc):
    if frappe.db.exists("Employee Salary", {"employee": doc.name, "year": now_datetime().year}):
        return

    employee_salary_doc = frappe.get_doc({"doctype": "Employee Salary", "employee": doc.name, "year": now_datetime().year})
    all_months = calendar.month_name[1:]
    items = []
    for month in all_months:
        key = frappe._dict({
            "month": month,
            "value": doc.ctc,
        })
        items.append(key)
    employee_salary_doc.update({"items": items})
    employee_salary_doc.insert().submit()

def set_account_holder_name(doc):
    if not doc.account_holder_name:
        doc.account_holder_name = doc.employee_name
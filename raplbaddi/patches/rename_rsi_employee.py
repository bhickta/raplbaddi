import frappe
from raplbaddi.overrides.employee import get_middle_no

def execute():
    employee_to_rename = get_branch_employee("Red Star Unit 2")
    print(employee_to_rename)
    employee_doc_to_rename = [frappe.get_doc("Employee", employee) for employee in employee_to_rename]
    rename_docs(employee_doc_to_rename)

def get_branch_employee(branch):
    return frappe.get_all(
        "Employee",
        filters={
            "branch": branch,
            "custom_employee_code": ["is", "set"]
        },
        pluck="name",
        order_by="creation asc"
    )

def rename_docs(docs):
    batch_size = 40
    for i in range(len(docs)):
        letter = chr(65 + (i // batch_size))
        new_name = f"RSI-{letter}-{i % batch_size + 1}"
        try:
            frappe.rename_doc("Employee", docs[i].name, new_name, force=True)
        except frappe.ValidationError as e:
            pass
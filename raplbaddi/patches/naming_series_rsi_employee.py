import frappe
from raplbaddi.utils import make_fields_set_only_once
def execute():
    branch_2_employees = frappe.get_all("Employee", {"branch": "Red Star Unit 2"}, pluck="name")
    for employee in branch_2_employees:
        doc = frappe.get_doc("Employee", employee)
        naming_series = doc.name.split("-")
        doc.naming_series = f"RSI-{naming_series[1]}-.#"
        make_fields_set_only_once(doc, ["naming_series"], False)
        doc.save()
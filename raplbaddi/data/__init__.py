import frappe
from .stock import data

def execute():
    frappe.get_doc(data).insert()

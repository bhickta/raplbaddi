import frappe
from raplbaddi.supportrapl.doctype.issuerapl.issuerapl import set_kilometers

def execute():
    issuerapl_docs = frappe.get_all(
        "IssueRapl", {
            "docstatus": 0,
            "creation": [">=", "2025-01-01"]
        }, pluck="name")
    for doc in issuerapl_docs:
        doc = frappe.get_doc("IssueRapl", doc)
        set_kilometers(doc)
        doc.save()
    
import frappe

def execute():
    return
    issuerapl_docs = frappe.get_all(
        "IssueRapl", {
            "docstatus": 0,
            "creation": [">=", "2025-01-01"],
            "aerial_kilometer": ["is", "set"]
        }, pluck="name")
    for doc in issuerapl_docs:
        doc = frappe.get_doc("IssueRapl", doc)
        doc.save()
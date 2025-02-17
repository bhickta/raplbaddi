import frappe

def execute():
    try:
        transaction_type = frappe.new_doc("Transaction Type")
        transaction_type.purpose = "Inward"
        transaction_type.name = "Service Centre Inward"
        transaction_type.save()
    except frappe.exceptions.DuplicateEntryError as e:
        pass
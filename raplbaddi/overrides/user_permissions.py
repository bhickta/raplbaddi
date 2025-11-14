import frappe

def validate(doc, method):
    if frappe.flags.ignore_permission:
        return
    if not frappe.session.user == "Administrator":
        frappe.throw(f"User <b>User Access Control Instead</b> to edit user access")
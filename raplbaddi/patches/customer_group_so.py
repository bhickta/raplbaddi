import frappe

def execute():
    so = frappe.get_all("Sales Order", fields=["name", "customer"])
    for s, c in so:
        customer_group = frappe.db.get_value("Customer", c, "customer_group")
        if customer_group:
            frappe.db.set_value("Sales Order", s, "customer_group", customer_group)
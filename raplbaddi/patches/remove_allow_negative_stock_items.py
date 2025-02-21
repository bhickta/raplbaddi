import frappe

def execute():
    remove_allow_negative_stock_items()

def remove_allow_negative_stock_items():
    query = f"""
        UPDATE `tabItem`
        SET allow_negative_stock = 1 
    """
    frappe.db.sql(query)
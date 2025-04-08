import frappe


def execute():
    query = """
        UPDATE `tabEmployee` SET `serial_number` = `index`    
    """
    frappe.db.sql(query)
import frappe

import frappe

def execute():
    frappe.db.sql("""
        UPDATE 
            `tabDaily Sales Customer` dsc
        INNER JOIN 
            `tabCustomer` c
        ON 
            dsc.customer = c.name
        SET 
            dsc.customer_name = c.customer_name
    """)
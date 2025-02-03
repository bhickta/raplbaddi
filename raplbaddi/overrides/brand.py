import frappe

def after_insert(doc, method):
    d = frappe.new_doc('Warehouse')
    d.warehouse_name = doc.brand
    d.parent_warehouse = 'B - RAPL'
    d.insert()

def after_delete(doc, method):
    frappe.delete_doc('Warehouse', doc.brand + ' - RAPL')

def after_rename(doc, method):
    frappe.rename_doc("Warehouse", doc.name, doc.name + "-WH-Defective", True)
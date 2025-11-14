import frappe
from raplbaddi.utils import make_fields_set_only_once


def validate(doc, method):
    validate_abbreviation(doc)

def validate_abbreviation(doc):
    if doc.is_new():
        return
    old_doc = frappe.get_doc("Supplier Group", doc.name)
    supplier_linked_to_group = frappe.get_all(
        "Customer", {"name": ["like", f"%{old_doc.abbreviation}%"]}, "name"
    )
    if not supplier_linked_to_group:
        return
    if old_doc.abbreviation != doc.abbreviation:
        supplier_names = '<br><li> '.join([supplier.name for supplier in supplier_linked_to_group])
        frappe.throw(
            f"Abbreviation cannot be changed as it is already used in Customers<br><li>{supplier_names}"
        )

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from raplbaddi.constants.buying import custom_fields

def execute():
    create_custom_fields(custom_fields)

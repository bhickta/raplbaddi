from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

custom_fields = {
    "Journal Entry Account": [
        {
            "is_system_generated": 1,
            "label": "Custom Reference Type",
            "fieldname": "custom_reference_type",
            "insert_after": "reference_type",
            "fieldtype": "Link",
            "options": "DocType",
            "allow_on_submit": 0,
        },
        {
            "is_system_generated": 1,
            "label": "Custom Reference Name",
            "fieldname": "custom_reference_name",
            "insert_after": "reference_name",
            "fieldtype": "Dynamic Link",
            "options": "custom_reference_type",
            "allow_on_submit": 0,
        },
    ]
}

def execute():
    create_custom_fields(custom_fields)
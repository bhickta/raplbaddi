from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

custom_fields = {
    "Item": [
        {
            "name": "Item-unit",
            "label": "Unit",
            "fieldname": "unit",
            "insert_after": "over_billing_allowance",
            "fieldtype": "Select",
            "options": "Unit 1\nUnit 2"
        },
        {
            "name": "Item-is_contractable",
            "label": "Is Contractable",
            "fieldname": "is_contractable",
            "insert_after": "include_item_in_manufacturing",
            "fieldtype": "Check",
        },
    ]
}


def execute():
    create_custom_fields(custom_fields)

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
    ],
    "UOM Conversion Detail": [
        {
            "name": "UOM Conversion Detail-conversion_multiple",
            "label": "Conversion Multiple",
            "fieldname": "conversion_multiple",
            "insert_after": "conversion_factor",
            "fieldtype": "Float",
            "read_only": 1,
            "reqd": 1,
        },
        {
            "name": "UOM Conversion Detail-conversion_multiple",
            "label": "Conversion Multiple",
            "fieldname": "conversion_multiple",
            "insert_after": "uom",
            "fieldtype": "Float",
            "read_only": 1,
            "in_list_view": 1,
            "columns": 2
        },
        {
            "name": "UOM Conversion Detail-base_uom",
            "label": "Base UOM",
            "fieldname": "base_uom",
            "insert_after": "conversion_multiple",
            "fieldtype": "Link",
            "options": "UOM",
            "read_only": 1,
            "in_list_view": 1,
            "columns": 1
        }
    ]
}


def execute():
    create_custom_fields(custom_fields)

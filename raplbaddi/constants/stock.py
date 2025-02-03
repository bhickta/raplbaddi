from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

custom_fields = {
    "Item": [
        {
            "is_system_generated": 1,
            "label": "CBM Section MM",
            "fieldname": "cbm_section",
            "insert_after": "uoms",
            "fieldtype": "Section Break",
            "collapsible": 1,
        },
        {
            "name": "Item-cbm_length",
            "label": "CBM Length",
            "fieldname": "cbm_length",
            "insert_after": "cbm_section",
            "fieldtype": "Float",
        },
        {
            "is_system_generated": 1,
            "fieldname": "cbm_cb_1",
            "insert_after": "cbm_length",
            "fieldtype": "Column Break",
        },
        {
            "name": "Item-cbm_width",
            "label": "CBM Width",
            "fieldname": "cbm_width",
            "insert_after": "cbm_cb_1",
            "fieldtype": "Float",
        },
        {
            "name": "Item-cbm_height",
            "label": "CBM Height",
            "fieldname": "cbm_height",
            "insert_after": "cbm_width",
            "fieldtype": "Float",
        },
        {
            "is_system_generated": 1,
            "fieldname": "cbm_section_1",
            "insert_after": "cbm_height",
            "fieldtype": "Section Break",
            "collapsible": 0,
        },
        {
            "name": "Item-cbm",
            "label": "CBM",
            "fieldname": "cbm",
            "insert_after": "cbm_height",
            "fieldtype": "Float",
            "read_only": 1,
            "precision": 9,
        },
        {
            "name": "Item-unit",
            "label": "Unit",
            "fieldname": "unit",
            "insert_after": "over_billing_allowance",
            "fieldtype": "Select",
            "options": "Unit 1\nUnit 2",
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
            "columns": 2,
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
            "columns": 1,
        },
    ],
    "Brand": [
        {
            "is_system_generated": 1,
            "label": "Warehouse",
            "fieldname": "warehouse",
            "insert_after": "supplier",
            "fieldtype": "Link",
            "options": "Warehouse",
        },
    ],
}


def execute():
    create_custom_fields(custom_fields)

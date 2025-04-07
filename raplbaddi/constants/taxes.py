from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

custom_taxes_fields = [
    {
        "fieldtype": "Section Break",
        "fieldname": "custom_tax_section_break",
        "insert_after": "net_total",
    },
    {
        "label": "Invoice Tax Rate",
        "fieldname": "custom_tax_rate",
        "insert_after": "custom_tax_section_break",
        "fieldtype": "Float",
        "no_copy": 1,
    },
    {
        "fieldtype": "Column Break",
        "fieldname": "custom_tax_column_break_1",
        "insert_after": "custom_tax_rate",
    },
    {
        "label": "Taxable Amount In Invoice",
        "fieldname": "custom_grand_total",
        "insert_after": "custom_tax_column_break_1",
        "fieldtype": "Currency",
        "no_copy": 1,
    },
]

doctypes = [
    "Purchase Order",
    "Purchase Receipt",
    "Purchase Invoice",
]
custom_fields = {}

for doctype in doctypes:
    for field in custom_taxes_fields:
        field["doctype"] = doctype
        custom_fields.setdefault(doctype, []).append(field)

def execute():
    create_custom_fields(custom_fields)

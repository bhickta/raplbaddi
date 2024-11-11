from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

custom_fields = {
    "Employee": [
        {
            "is_system_generated": 1,
            "label": "Father's Name",
            "fieldname": "father_name",
            "insert_after": "gender",
            "fieldtype": "Data",
            "reqd": 1,
        },
        {
            "is_system_generated": 1,
            "label": "Aadhar Card",
            "fieldname": "aadhar_card",
            "insert_after": "father_name",
            "fieldtype": "Data",
            "reqd": 1,
        },
    ],
    "Shift Type": [
        {
            "is_system_generated": 1,
            "label": "Time Allowance",
            "fieldname": "time_allowance",
            "insert_after": "end_time",
            "fieldtype": "Float",
            "description": "In Seconds",
            "default": "900",
            "read_only": 0,
            "hidden": 0,
            "no_copy": 0,
        },
        {
            "is_system_generated": 1,
            "label": "Has Overtime",
            "fieldname": "has_overtime",
            "insert_after": "time_allowance",
            "fieldtype": "Check",
            "read_only": 0,
            "hidden": 0,
            "no_copy": 0,
        },
    ],
}


def execute():
    create_custom_fields(custom_fields)


def get_property_setters():
    property_setters = []
    for field in ["bank_name", "bank_ac_no", "iban"]:
        property_setters.append(
                {
            "name": f"Employee-{field}-depends_on",
            "owner": "Administrator",
            "docstatus": 0,
            "idx": 0,
            "is_system_generated": 1,
            "doctype_or_field": "DocField",
            "doc_type": "Employee",
            "field_name": f"{field}",
            "property": "depends_on",
            "property_type": "Code",
            "value": "",
            "doctype": "Property Setter",
        })

    return property_setters
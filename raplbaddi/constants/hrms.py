from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

custom_fields = {
    "Employee": [
        {
            "is_system_generated": 1,
            "label": "IDX",
            "fieldname": "index",
            "insert_after": "basic_details_tab",
            "fieldtype": "Int",
            "reqd": 1,
        },
        {
            "is_system_generated": 1,
            "label": "Custom Employee Code",
            "fieldname": "custom_employee_code",
            "insert_after": "branch",
            "fieldtype": "Data",
            "reqd": 0,
        },
        {
            "is_system_generated": 1,
            "label": "Sub Department",
            "fieldname": "sub_department",
            "insert_after": "department",
            "fieldtype": "Link",
            "options": "Sub Department",
            "reqd": 0,
        },
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
            "label": "ESIC Number",
            "fieldname": "esic_number",
            "insert_after": "provident_fund_account",
            "fieldtype": "Data",
            "reqd": 0,
        },
        {
            "is_system_generated": 1,
            "label": "Aadhar Card",
            "fieldname": "aadhar_card",
            "insert_after": "father_name",
            "fieldtype": "Data",
            "reqd": 1,
        },
        {
            "is_system_generated": 1,
            "label": "Account Holder Name",
            "fieldname": "account_holder_name",
            "insert_after": "bank_name",
            "fieldtype": "Data",
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
    "Sales Person": [
        {
            "is_system_generated": 1,
            "label": "Travel Rate",
            "fieldname": "travel_rate",
            "insert_after": "employee",
            "fieldtype": "Currency",
            "default": "9",
            "reqd": 0,
        },
    ],
}


def execute():
    create_custom_fields(custom_fields)


def get_property_setters():
    property_setters = []
    for field in ["bank_name", "bank_ac_no", "ifsc_code", "micr_code"]:
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
            }
        )

    property_setters.extend(
        [
            {
                "name": f"Employee-provident_fund_account-label",
                "owner": "Administrator",
                "docstatus": 0,
                "idx": 0,
                "is_system_generated": 1,
                "doctype_or_field": "DocField",
                "doc_type": "Employee",
                "field_name": f"provident_fund_account",
                "property": "label",
                "property_type": "Data",
                "value": "PF Number",
                "doctype": "Property Setter",
            }
        ]
    )

    return property_setters

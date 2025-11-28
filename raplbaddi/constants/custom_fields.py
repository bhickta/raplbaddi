from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

custom_fields = {
    "Material Request": [
        {
            "dt": "Material Request",
            "is_system_generated": 1,
            "label": "Department",
            "fieldname": "department",
            "insert_after": "buying_price_list",   
            "fieldtype": "Link",
            "options": "Department",
            "reqd": 1,                              
            "in_list_view": 1,
            "in_standard_filter": 1,
            "fetch_from": "requested_by.department",
            "fetch_if_empty": 1,
            "allow_on_submit": 0,
        },
        {
            "dt": "Material Request",
            "is_system_generated": 1,
            "label": "Supervisor",
            "fieldname": "supervisor",
            "insert_after": "department",          
            "fieldtype": "Link",
            "options": "Employee",
            "reqd": 1,                              
            "in_list_view": 1,
            "in_standard_filter": 1,
            "fetch_from": "requested_by.reports_to",
            "fetch_if_empty": 1,
            "allow_on_submit": 0,
        }
    ]
}
def execute():
    create_custom_fields(custom_fields)

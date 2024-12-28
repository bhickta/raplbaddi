import frappe

def create_role(role):
    role.update({
        "doctype": "Role",
    })
    role = frappe.get_doc(role)
    role.insert()

roles = [
    {
        "role_name": "Salary Auditor",
        "desk_access": 0,
    },
    {
        "role_name": "Transportation Manager",
        "desk_access": 0,
    },
]


def execute():
    for role in roles:
        if frappe.db.exists("Role", role):
            continue
        create_role(role)
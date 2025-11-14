import frappe

def execute():
    set_branches()
    set_branch_to_red_for_filtered_docs("Material Receipt Note")
    set_branch_to_red_for_filtered_docs("Delivery Note")

def set_branches():
    branches = ["Real Appliances Private Limited", "Red Star Unit 2"]
    for branch in branches:
        if not frappe.db.exists("Branch", branch):
            frappe.get_doc({
                "doctype": "Branch",
                "branch": branch
            }).insert()

def set_branch_to_red_for_filtered_docs(doctype):
    query = f"""
        UPDATE `tab{doctype}`
        SET branch = 'Real Appliances Private Limited'
        WHERE creation < '2024-09-23'
    """
    frappe.db.sql(query)
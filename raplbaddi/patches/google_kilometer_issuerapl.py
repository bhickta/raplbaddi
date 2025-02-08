import frappe

def execute():
    issues = frappe.db.sql(f"""
        SELECT name
        FROM `tabIssueRapl`
        WHERE kilometer <= aerial_kilometer
        AND kilometer > 0
        AND docstatus = 0
    """, as_dict=1, pluck="name")
    for issue in issues:
        doc = frappe.get_doc("IssueRapl", issue)
        doc.kilometer = 2 * doc.kilometer
        doc.save()
    frappe.db.commit()
import frappe

def execute():
    issues = frappe.get_all("IssueRapl", fields=["name", "issue_type"])

    if not issues:
        return

    values = []
    for issue in issues:
        unique_name = frappe.generate_hash(length=10)
        values.append(f"('{unique_name}', '{issue['name']}', 'issuerapl_items', 'IssueRapl', '{issue['issue_type']}')")

    if values:
        values_str = ", ".join(values)
        query = f"""
            INSERT INTO `tabIssueRapl Item` (`name`, `parent`, `parentfield`, `parenttype`, `issue_type`)
            VALUES {values_str}
        """
        frappe.db.sql(query)
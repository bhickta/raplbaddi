import frappe

def execute(filters=None):
    filters = filters or {}

    # -------------------- COLUMNS --------------------
    columns = [
        {"label": "Issue ID", "fieldname": "issue_id", "fieldtype": "Link", "options": "IssueRapl", "width": 140},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": "Brand Name", "fieldname": "brand_name", "fieldtype": "Data", "width": 150},
        {"label": "Geyser Capacity", "fieldname": "geyser_capacity", "fieldtype": "Data", "width": 120},
        {"label": "Model", "fieldname": "model", "fieldtype": "Data", "width": 120},
        {"label": "Customer Address", "fieldname": "customer_address", "fieldtype": "Small Text", "width": 240},
        {"label": "State", "fieldname": "customer_address_state", "fieldtype": "Data", "width": 120},
        {"label": "Issue Type", "fieldname": "issue_type", "fieldtype": "Data", "width": 150},
        {"label": "Sub Issue", "fieldname": "sub_issue", "fieldtype": "Data", "width": 180},
    ]

    # -------------------- CONDITIONS --------------------
    conditions = "1=1"

    if filters.get("status"):
        conditions += f" AND issue.status = '{filters['status']}'"

    if filters.get("brand_name"):
        conditions += f" AND issue.brand_name LIKE '%{filters['brand_name']}%'"

    if filters.get("geyser_capacity"):
        conditions += f" AND issue.geyser_capacity LIKE '%{filters['geyser_capacity']}%'"

    if filters.get("model"):
        conditions += f" AND issue.model LIKE '%{filters['model']}%'"

    if filters.get("customer_address_state"):
        conditions += f" AND issue.customer_address_state LIKE '%{filters['customer_address_state']}%'"

    # -------------------- MAIN QUERY --------------------
    query = f"""
        SELECT
            issue.name AS issue_id,
            issue.status,
            issue.brand_name,
            issue.geyser_capacity,
            issue.model,
            issue.customer_address,
            issue.customer_address_state,
            child.issue_type,
            child.sub_issue
        FROM
            `tabIssueRapl` issue
        LEFT JOIN 
            `tabIssueRapl Item` child 
            ON child.parent = issue.name
        WHERE
            {conditions}
        ORDER BY issue.creation DESC
    """

    data = frappe.db.sql(query, as_dict=True)

    return columns, data

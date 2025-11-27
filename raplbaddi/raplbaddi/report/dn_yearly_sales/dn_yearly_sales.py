import frappe

def execute(filters=None):
    filters = filters or {}

    fy_24_25_start = "2024-04-01"
    fy_24_25_end   = "2025-03-31"
    fy_25_26_start = "2025-04-01"
    fy_25_26_end   = "2026-03-31"

    item_group = filters.get("item_group")
    brand = filters.get("brand")
    customer = filters.get("customer")

    # ---------------------------
    # STEP 1: only filtered items ka data lo
    # ---------------------------
    conditions = ["dn.docstatus = 1"]

    if item_group:
        conditions.append("dni.item_group = %(item_group)s")
    if brand:
        conditions.append("dni.brand = %(brand)s")
    if customer:
        conditions.append("dn.customer = %(customer)s")

    where_clause = " AND ".join(conditions)

    rows = frappe.db.sql(f"""
        SELECT
            dn.customer,
            dn.customer_name,
            dn.customer_group,
            dni.qty,
            dn.posting_date
        FROM `tabDelivery Note Item` dni
        JOIN `tabDelivery Note` dn ON dn.name = dni.parent
        WHERE {where_clause}
    """, {
        "item_group": item_group,
        "brand": brand,
        "customer": customer
    }, as_dict=True)

    # ---------------------------
    # STEP 2: customer-wise yearly qty
    # ---------------------------
    cust_map = {}

    for r in rows:
        cust = r.customer

        if cust not in cust_map:
            cust_map[cust] = {
                "customer_name": r.customer_name,
                "customer_group": r.customer_group,
                "fy_24_25": 0,
                "fy_25_26": 0
            }

        posting = str(r.posting_date)

        if fy_24_25_start <= posting <= fy_24_25_end:
            cust_map[cust]["fy_24_25"] += r.qty

        if fy_25_26_start <= posting <= fy_25_26_end:
            cust_map[cust]["fy_25_26"] += r.qty

    # ---------------------------
    # FINAL DATA
    # ---------------------------
    data = []
    for cust, val in cust_map.items():
        data.append({
            "customer_name": val["customer_name"],
            "customer_group": val["customer_group"],
            "fy_24_25": val["fy_24_25"],
            "fy_25_26": val["fy_25_26"]
        })

    columns = [
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 220},
        {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Data", "width": 150},
        {"label": "FY 24-25 Qty", "fieldname": "fy_24_25", "fieldtype": "Float", "width": 140},
        {"label": "FY 25-26 Qty", "fieldname": "fy_25_26", "fieldtype": "Float", "width": 140},
    ]

    return columns, data

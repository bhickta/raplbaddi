import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    item_group = filters.get("item_group")

    # FY ranges
    fy_24_25_start = "2024-04-01"
    fy_24_25_end   = "2025-03-31"

    fy_25_26_start = "2025-04-01"
    fy_25_26_end   = "2026-03-31"

    # ---------------- FETCH CUSTOMERS WHO HAVE SALES IN SELECTED ITEM GROUP ----------------
    customers = frappe.db.sql("""
        SELECT DISTINCT 
            dn.customer AS name,
            dn.customer_name,
            c.customer_group,
            dni.item_group
        FROM `tabDelivery Note Item` dni
        JOIN `tabDelivery Note` dn ON dn.name = dni.parent
        JOIN `tabCustomer` c ON c.name = dn.customer
        WHERE dn.docstatus = 1
          {item_group_filter}
    """.format(
        item_group_filter = "AND dni.item_group = %s" if item_group else ""
    ), ([item_group] if item_group else []), as_dict=True)

    # Create customer map
    cust_map = {c.name: c for c in customers}

    # ---------------- FY 24-25 SALES ----------------
    fy24_data = frappe.db.sql("""
        SELECT 
            dn.customer,
            SUM(dni.qty) AS qty
        FROM `tabDelivery Note Item` dni
        JOIN `tabDelivery Note` dn ON dn.name = dni.parent
        WHERE dn.docstatus = 1
          AND dn.posting_date BETWEEN %s AND %s
          {item_group_filter}
        GROUP BY dn.customer
    """.format(
        item_group_filter = "AND dni.item_group = %s" if item_group else ""
    ), ([fy_24_25_start, fy_24_25_end] + ([item_group] if item_group else [])), as_dict=True)

    fy24_map = {d.customer: d.qty for d in fy24_data}

    # ---------------- FY 25-26 SALES ----------------
    fy25_data = frappe.db.sql("""
        SELECT 
            dn.customer,
            SUM(dni.qty) AS qty
        FROM `tabDelivery Note Item` dni
        JOIN `tabDelivery Note` dn ON dn.name = dni.parent
        WHERE dn.docstatus = 1
          AND dn.posting_date BETWEEN %s AND %s
          {item_group_filter}
        GROUP BY dn.customer
    """.format(
        item_group_filter = "AND dni.item_group = %s" if item_group else ""
    ), ([fy_25_26_start, fy_25_26_end] + ([item_group] if item_group else [])), as_dict=True)

    fy25_map = {d.customer: d.qty for d in fy25_data}

    # ---------------- FINAL DATA ----------------
    data = []
    for cust_id, cust in cust_map.items():
        data.append({
            "customer_name": cust.customer_name,
            "customer_group": cust.customer_group,

            # ⭐⭐⭐ MAIN FIX ⭐⭐⭐
            "item_group": item_group if item_group else cust.item_group,

            "fy_24_25": fy24_map.get(cust_id, 0) or 0,
            "fy_25_26": fy25_map.get(cust_id, 0) or 0
        })

    # ---------------- COLUMNS ----------------
    columns = [
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Data", "width": 150},
        {"label": "Item Group", "fieldname": "item_group", "fieldtype": "Data", "width": 150},
        {"label": "FY 24-25 Qty", "fieldname": "fy_24_25", "fieldtype": "Float", "width": 130},
        {"label": "FY 25-26 Qty", "fieldname": "fy_25_26", "fieldtype": "Float", "width": 130},
    ]

    return columns, data

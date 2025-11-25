import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    # ---------- FILTERS ----------
    item_group = filters.get("item_group")

    # ---------- FY DATE RANGES ----------
    fy_24_25_start = "2024-04-01"
    fy_24_25_end   = "2025-03-31"

    fy_25_26_start = "2025-04-01"
    fy_25_26_end   = "2026-03-31"

    # ---------- ALL CUSTOMERS ----------
    customers = frappe.get_all("Customer", fields=["name", "customer_name", "customer_group"])
    customer_map = {c.name: c for c in customers}

    # ---------- CUSTOMER ITEM GROUP FETCH ----------
    customer_item_groups = frappe.db.sql("""
        SELECT DISTINCT dn.customer, dni.item_group
        FROM `tabDelivery Note Item` dni
        JOIN `tabDelivery Note` dn ON dn.name = dni.parent
        WHERE dn.docstatus = 1
        {item_group_filter}
    """.format(
        item_group_filter = "AND dni.item_group = %s" if item_group else ""
    ), ([item_group] if item_group else []), as_dict=True)

    # Store FIRST item group per customer
    item_group_map = {}
    for row in customer_item_groups:
        if row.customer not in item_group_map:
            item_group_map[row.customer] = row.item_group

    # ---------- SALES FOR FY 24-25 ----------
    fy24_25_data = frappe.db.sql("""
        SELECT 
            dn.customer,
            SUM(dni.qty) as qty
        FROM `tabDelivery Note Item` dni
        JOIN `tabDelivery Note` dn ON dn.name = dni.parent
        WHERE dn.docstatus = 1
          AND dn.posting_date BETWEEN %s AND %s
          {item_group_filter}
        GROUP BY dn.customer
    """.format(
        item_group_filter = "AND dni.item_group = %s" if item_group else ""
    ), ([fy_24_25_start, fy_24_25_end] + ([item_group] if item_group else [])), as_dict=True)

    fy24_map = {d.customer: d.qty for d in fy24_25_data}

    # ---------- SALES FOR FY 25-26 ----------
    fy25_26_data = frappe.db.sql("""
        SELECT 
            dn.customer,
            SUM(dni.qty) as qty
        FROM `tabDelivery Note Item` dni
        JOIN `tabDelivery Note` dn ON dn.name = dni.parent
        WHERE dn.docstatus = 1
          AND dn.posting_date BETWEEN %s AND %s
          {item_group_filter}
        GROUP BY dn.customer
    """.format(
        item_group_filter = "AND dni.item_group = %s" if item_group else ""
    ), ([fy_25_26_start, fy_25_26_end] + ([item_group] if item_group else [])), as_dict=True)

    fy25_map = {d.customer: d.qty for d in fy25_26_data}

    # ---------- FINAL DATA ----------
    data = []

    for cust_id, cust in customer_map.items():
        row = {
            "customer_name": cust.customer_name,
            "customer_group": cust.customer_group,
            "item_group": item_group_map.get(cust_id, ""),     # ✔ Item Group
            "fy_24_25": fy24_map.get(cust_id, 0) or 0,         # FY 24-25
            "fy_25_26": fy25_map.get(cust_id, 0) or 0          # FY 25-26
        }
        data.append(row)

    # ---------- COLUMNS ----------
    columns = [
        {"label": "Customer Name", "fieldname": "customer_name", "fieldtype": "Data", "width": 200},
        {"label": "Customer Group", "fieldname": "customer_group", "fieldtype": "Data", "width": 150},
        {"label": "Item Group", "fieldname": "item_group", "fieldtype": "Data", "width": 150},   # ✔ NOW CORRECT
        {"label": "FY 24-25 Qty", "fieldname": "fy_24_25", "fieldtype": "Float", "width": 120},
        {"label": "FY 25-26 Qty", "fieldname": "fy_25_26", "fieldtype": "Float", "width": 120},
    ]

    return columns, data

import frappe

def execute(filters=None):
    filters = filters or {}
    conditions = []

    # Toggle view mode
    view_by_group = frappe.parse_json(filters.get("view_by_group") or 0)

    # STATUS FILTER
    selected_status = filters.get("status")
    if selected_status == "Submitted":
        conditions.append("dn.docstatus = 1")
    elif selected_status == "Cancelled":
        conditions.append("dn.docstatus = 2")
    else:
        conditions.append("dn.docstatus IN (1, 2)")

    # SAFELY ESCAPED FILTERS
    if filters.get("item_group"):
        conditions.append(f"dni.item_group = {frappe.db.escape(filters.get('item_group'))}")
    if filters.get("customer"):
        conditions.append(f"dn.customer = {frappe.db.escape(filters.get('customer'))}")
    if filters.get("brand"):
        conditions.append(f"dni.brand = {frappe.db.escape(filters.get('brand'))}")
    if filters.get("from_date"):
        conditions.append(f"dn.posting_date >= {frappe.db.escape(filters.get('from_date'))}")
    if filters.get("to_date"):
        conditions.append(f"dn.posting_date <= {frappe.db.escape(filters.get('to_date'))}")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    # FIXED SQL — NO DUPLICATE QTY NOW
    dn_query = f"""
        SELECT
            dn.name AS dn_name,
            dn.customer AS customer,
            dn.customer_name AS customer_name,
            dn.customer_group AS customer_group,
            SUM(dni.qty) AS dn_qty,
            GROUP_CONCAT(DISTINCT dni.item_code SEPARATOR ', ') AS item_codes,
            GROUP_CONCAT(DISTINCT dni.brand SEPARATOR ', ') AS brand_names,
            IFNULL(dn.amount, 0) AS total_freight,
            CASE 
                WHEN dn.docstatus = 1 THEN 'Submitted'
                WHEN dn.docstatus = 2 THEN 'Cancelled'
                ELSE 'Draft'
            END AS status
        FROM `tabDelivery Note` dn
        JOIN `tabDelivery Note Item` dni ON dn.name = dni.parent
        LEFT JOIN `tabItem` i ON i.name = dni.item_code
        {where_clause}
        GROUP BY dn.name
    """

    dn_data = frappe.db.sql(dn_query, as_dict=True)

    # CUSTOMER-WISE AGGREGATION
    customer_totals = {}

    for row in dn_data:
        cust = row.customer

        if cust not in customer_totals:
            customer_totals[cust] = {
                "customer_name": row.customer_name,
                "customer_group": row.customer_group,
                "item_codes": set(),
                "brand_names": set(),
                "total_qty": 0,
                "total_freight": 0,
                "status": row.status,
            }

        # FIX — add only dn_qty (no duplication)
        customer_totals[cust]["total_qty"] += row.dn_qty
        customer_totals[cust]["total_freight"] += row.total_freight

        if row.item_codes:
            customer_totals[cust]["item_codes"].update(i.strip() for i in row.item_codes.split(", "))
        if row.brand_names:
            customer_totals[cust]["brand_names"].update(b.strip() for b in row.brand_names.split(", "))

    # VIEW BY GROUP MODE
    if view_by_group:
        group_map = {}

        for cust, vals in customer_totals.items():
            grp = vals["customer_group"] or "Unknown"

            if grp not in group_map:
                group_map[grp] = {
                    "customer_group": grp,
                    "total_qty": 0,
                    "total_freight": 0,
                }

            group_map[grp]["total_qty"] += vals["total_qty"]
            group_map[grp]["total_freight"] += vals["total_freight"]

        data = []
        for grp, vals in group_map.items():
            qty = vals["total_qty"]
            freight = vals["total_freight"]
            freight_per_item = round(freight / qty, 2) if qty else 0

            data.append({
                "customer_group": grp,
                "total_qty": qty,
                "total_freight": freight,
                "freight_per_item": freight_per_item,
            })

        columns = [
            {"fieldname": "customer_group", "label": "Customer Group", "fieldtype": "Data", "width": 220},
            {"fieldname": "total_qty", "label": "Total Qty", "fieldtype": "Float", "width": 140},
            {"fieldname": "total_freight", "label": "Total Freight", "fieldtype": "Currency", "width": 150},
            {"fieldname": "freight_per_item", "label": "Freight/Item", "fieldtype": "Currency", "width": 150},
        ]

        return columns, data

    # NORMAL CUSTOMER-WISE OUTPUT
    data = []
    for cust, vals in customer_totals.items():
        qty = vals["total_qty"]
        freight = vals["total_freight"]

        data.append({
            "customer_name": vals["customer_name"],
            "customer_group": vals["customer_group"],
            "brand": ", ".join(sorted(vals["brand_names"])) or "-",
            "item_code": ", ".join(sorted(vals["item_codes"])) or "-",
            "total_qty": qty,
            "total_freight": freight,
            "freight_per_item": round(freight / qty, 2) if qty else 0,
            "status": vals["status"],
        })

    columns = [
        {"fieldname": "customer_name", "label": "Customer Name", "fieldtype": "Data", "width": 250},
        {"fieldname": "customer_group", "label": "Customer Group", "fieldtype": "Data", "width": 150},
        {"fieldname": "brand", "label": "Brand", "fieldtype": "Data", "width": 150},
        {"fieldname": "item_code", "label": "Item Code(s)", "fieldtype": "Data", "width": 240},
        {"fieldname": "total_qty", "label": "Total Qty", "fieldtype": "Float", "width": 120},
        {"fieldname": "total_freight", "label": "Total Freight", "fieldtype": "Currency", "width": 140},
        {"fieldname": "freight_per_item", "label": "Freight per Item", "fieldtype": "Currency", "width": 140},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 110},
    ]

    return columns, data

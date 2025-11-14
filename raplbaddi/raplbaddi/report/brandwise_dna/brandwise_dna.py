import frappe

def execute(filters=None):
    filters = filters or {}
    conditions = []

    # STATUS FILTER
    selected_status = filters.get("status")
    if selected_status == "Submitted":
        conditions.append("dn.docstatus = 1")
    elif selected_status == "Cancelled":
        conditions.append("dn.docstatus = 2")
    else:
        conditions.append("dn.docstatus IN (1, 2)")

    # Additional filters
    if filters.get("item_group"):
        conditions.append(f"i.item_group = {frappe.db.escape(filters.get('item_group'))}")
    if filters.get("customer"):
        conditions.append(f"dn.customer = {frappe.db.escape(filters.get('customer'))}")
    if filters.get("brand"):
        conditions.append(f"dni.brand = {frappe.db.escape(filters.get('brand'))}")
    if filters.get("from_date"):
        conditions.append(f"dn.posting_date >= {frappe.db.escape(filters.get('from_date'))}")
    if filters.get("to_date"):
        conditions.append(f"dn.posting_date <= {frappe.db.escape(filters.get('to_date'))}")

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # STEP 1: Query
    dn_query = f"""
        SELECT
            dn.name AS dn_name,
            dn.customer AS customer,
            dn.customer_name AS customer_name,
            GROUP_CONCAT(DISTINCT dni.item_code SEPARATOR ', ') AS item_codes,
            GROUP_CONCAT(DISTINCT dni.brand SEPARATOR ', ') AS brand_names,
            SUM(dni.qty) AS total_qty,
            IFNULL(dn.amount, 0) AS total_freight,
            CASE 
                WHEN dn.docstatus = 1 THEN 'Submitted'
                WHEN dn.docstatus = 2 THEN 'Cancelled'
                ELSE 'Draft'
            END AS status
        FROM `tabDelivery Note` dn
        LEFT JOIN `tabDelivery Note Item` dni ON dn.name = dni.parent
        LEFT JOIN `tabItem` i ON i.name = dni.item_code
        {where_clause}
        GROUP BY dn.name, dn.customer, dn.customer_name, dn.amount, dn.docstatus
    """

    dn_data = frappe.db.sql(dn_query, as_dict=True)

    # STEP 2: Aggregate per customer
    customer_totals = {}
    for row in dn_data:
        cust = row.get("customer") or "Unknown"

        if cust not in customer_totals:
            customer_totals[cust] = {
                "customer_name": row.get("customer_name"),
                "item_codes": set(),
                "brand_names": set(),
                "total_qty": 0,
                "total_freight": 0,
                "status": row.get("status"),
            }

        customer_totals[cust]["total_qty"] += row.get("total_qty") or 0
        customer_totals[cust]["total_freight"] += row.get("total_freight") or 0

        if row.get("item_codes"):
            for item in row["item_codes"].split(", "):
                customer_totals[cust]["item_codes"].add(item.strip())

        if row.get("brand_names"):
            for brand in row["brand_names"].split(", "):
                customer_totals[cust]["brand_names"].add(brand.strip())

    # STEP 3: Final output
    data = []
    for cust, vals in customer_totals.items():
        qty = vals["total_qty"]
        freight = vals["total_freight"]
        freight_per_item = round(freight / qty, 2) if qty else 0

        data.append({
            "customer_name": vals["customer_name"],
            "brand": ", ".join(sorted(vals["brand_names"])) or "-",
            "item_code": ", ".join(sorted(vals["item_codes"])) or "-",
            "total_qty": qty,
            "total_freight": freight,
            "freight_per_item": freight_per_item,
            "status": vals["status"],
        })

    # STEP 4: Columns
    columns = [
        {"fieldname": "customer_name", "label": "Customer Name", "fieldtype": "Data", "width": 250},
        {"fieldname": "brand", "label": "Brand", "fieldtype": "Data", "width": 150},
        {"fieldname": "item_code", "label": "Item Code(s)", "fieldtype": "Data", "width": 250},
        {"fieldname": "total_qty", "label": "Total Quantity", "fieldtype": "Float", "width": 130},
        {"fieldname": "total_freight", "label": "Total Freight", "fieldtype": "Currency", "width": 150},
        {"fieldname": "freight_per_item", "label": "Freight per Item", "fieldtype": "Currency", "width": 150},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 120},
    ]

    return columns, data

# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    # --- Build dynamic filter conditions ---
    conditions = ""
    if filters.get("brand"):
        conditions += " AND i.brand = %(brand)s"
    if filters.get("customer"):
        conditions += " AND dn.customer = %(customer)s"
    if filters.get("item_code"):
        conditions += " AND dni.item_code = %(item_code)s"

    # --- Main query: Fetch Delivery Note Item data with Brand, Customer, and Item ---
    data = frappe.db.sql(f"""
        SELECT
            i.brand AS brand,
            dn.customer AS customer,
            dni.item_code AS item_code,
            dni.item_name AS item_name,
            SUM(dni.qty) AS total_qty
        FROM
            `tabDelivery Note Item` dni
            INNER JOIN `tabDelivery Note` dn ON dni.parent = dn.name
            INNER JOIN `tabItem` i ON dni.item_code = i.name
        WHERE
            dn.docstatus = 1 {conditions}
        GROUP BY
            i.brand, dn.customer, dni.item_code, dni.item_name
        ORDER BY
            i.brand, dn.customer
    """, filters, as_dict=1)

    # --- Calculate Brand-wise Totals and Unique Customer List ---
    brand_summary = {}
    for row in data:
        brand = row.get("brand") or "No Brand"
        if brand not in brand_summary:
            brand_summary[brand] = {"total_qty": 0, "customers": set()}
        brand_summary[brand]["total_qty"] += row["total_qty"]
        brand_summary[brand]["customers"].add(row["customer"])

    # --- Calculate overall total quantity (for percentage calculation) ---
    total_all_brands = sum(details["total_qty"] for details in brand_summary.values()) or 1

    # --- Sort brands by total quantity descending ---
    sorted_brands = sorted(
        brand_summary.items(),
        key=lambda x: x[1]["total_qty"],
        reverse=True
    )

    # --- Prepare summary rows (Brand Totals) ---
    summary_rows = []
    for brand, details in sorted_brands:
        # Convert customer set to a comma-separated string
        customer_list = ", ".join(sorted(details["customers"]))
        percent = round((details["total_qty"] / total_all_brands) * 100, 2)

        summary_rows.append({
            "brand": f"{brand} (Total)",
            "customer": f"{customer_list} ({len(details['customers'])} Customers)",
            "item_code": "",
            "item_name": f"{percent}% of Total",
            "total_qty": details["total_qty"]
        })

    # --- Combine detailed data and summary rows ---
    final_data = data + summary_rows

    # --- Define report columns ---
    columns = [
        {"label": "Brand", "fieldname": "brand", "fieldtype": "Link", "options": "Brand", "width": 150},
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 280},
        {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
        {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 220},
        {"label": "Total Qty", "fieldname": "total_qty", "fieldtype": "Float", "width": 120}
    ]

    return columns, final_data

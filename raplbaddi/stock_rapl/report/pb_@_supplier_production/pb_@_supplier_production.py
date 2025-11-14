# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns, data = [], []
    columns, data = get_columns(filters=None), get_data(filters=None)
    return columns, data

def get_columns(filters):
    columns = [
        {
            "label": "Latest PO Date",
            "fieldtype": "Date",
            "width": 150,
            "fieldname": "po_date",
        },
        {
            "label": "Box Name",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150,
            "fieldname": "box_name",
        },
        {"label": "Model", "fieldtype": "Data", "width": 140, "fieldname": "model"},
        {
            "label": "Capacity",
            "fieldtype": "Int",
            "width": 80,
            "fieldname": "capacity",
            "disable_total": True,
        },
        {
            "label": "Stock @Supplier",
            "fieldtype": "Int",
            "width": 140,
            "fieldname": "supplier_stock",
        },
        {
            "label": "Order for production",
            "fieldtype": "Int",
            "width": 140,
            "fieldname": "order_for_production",
        },
        {
            "label": "Over Dispatch",
            "fieldtype": "Int",
            "width": 140,
            "fieldname": "over_dispatch",
        },
        {"label": "PO", "fieldtype": "Data", "width": 80, "fieldname": "po_link"},
    ]
    return columns


def get_data(filters):
    query = f"""
		SELECT
			po.transaction_date AS po_date,
			i.name AS box_name,
			i.capacity AS capacity,
			i.geyser_model AS model,
			SUM(poi.qty - poi.received_qty + IF(poi.received_qty > poi.qty, poi.received_qty - poi.qty, 0)) AS order_for_production,
			SUM(poi.planned_dispatch_qty - poi.received_qty + IF(poi.received_qty > poi.qty, poi.received_qty - poi.qty, 0)) AS `Order For Dispatch:Int:150`,
			COALESCE(
				(SELECT GREATEST(b.actual_qty, 0) FROM `tabBin` AS b WHERE b.item_code = i.name AND b.warehouse = 'Jai Ambey Industries - RAPL'),
				0
			) AS supplier_stock,
			SUM(poi.received_qty) AS `Dispatched Qty:Int:120`,
			GREATEST(
				SUM(
					GREATEST(COALESCE(poi.qty, 0), 0) - GREATEST(COALESCE(poi.received_qty, 0), 0)
				) - GREATEST(
					IFNULL(
						(SELECT b1.actual_qty FROM `tabBin` AS b1 WHERE b1.item_code = i.name AND b1.warehouse = 'Jai Ambey Industries - RAPL'),
						0
					),
					0
				),
				0
			) AS `Pending For Production:Int:170`,
			GREATEST(SUM(poi.planned_dispatch_qty - poi.received_qty), 0) AS `Pending For Dispatch:Int:160`,
			GROUP_CONCAT(DISTINCT CONCAT('<a href="https://raplbaddi.com/app/purchase-order/', po.name, '">', po.name, '</a>')) AS po_link
		FROM
			`tabPurchase Order` AS po
			LEFT JOIN `tabPurchase Order Item` AS poi ON poi.parent = po.name
			LEFT JOIN `tabItem` AS i ON i.name = poi.item_code
		WHERE
			po.supplier = 'Jai Ambey Industries'
			AND po.docstatus = 1
			AND poi.from_warehouse = 'Jai Ambey Industries - RAPL'
		GROUP BY
			poi.item_code
		ORDER BY
			po.transaction_date DESC
	"""
    result = frappe.db.sql(query, as_dict=True)
    return result


# SUM(IF(poi.received_qty > poi.qty, poi.received_qty - poi.qty, 0)) AS over_dispatch,

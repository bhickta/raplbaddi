# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    return get_columns(filters), get_data(filters)


def get_columns(filters):
    columns = [
        # {
        #     "label": "Count",
        #     "fieldname": "count",
        #     "fieldtype": "int",
        #     "width": 110,
        # },
        {
            "label": "Sales Order",
            "fieldname": "sales_order",
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 110,
        },
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 110,
        },
        {
            "label": "Item",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 180,
        },
        {
            "label": "Brand",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 110,
        },
        # {
        #     "label": "Ordered",
        #     "fieldname": "ordered_qty",
        #     "fieldtype": "Int",
        #     "width": 110,
        # },
        # {
        #     "label": "Delivered",
        #     "fieldname": "delivered_qty",
        #     "fieldtype": "Int",
        #     "width": 110,
        # },
        {
            "label": "Stock @FG",
            "fieldname": "actual_qty",
            "fieldtype": "Int",
            "width": 110,
        },
        {
            "label": "Pending @CU",
            "fieldname": "pending_qty",
            "fieldtype": "Int",
            "width": 110,
        },
        {
            "label": "Fullfill @CU",
            "fieldname": "fullfill_cu",
            "fieldtype": "int",
            "width": 110,
        },
        {
            "label": "Pending @SOs",
            "fieldname": "need",
            "fieldtype": "int",
            "width": 110,
        },
        {
            "label": "Fullfill @SOs",
            "fieldname": "fullfill_so",
            "fieldtype": "int",
            "width": 110,
        },
        # {
        #     "label": "Reserved?",
        #     "fieldname": "reserved_status",
        #     "fieldtype": "int",
        #     "width": 110,
        # },
        # {
        #     "label": "Reserved",
        #     "fieldname": "sales_order_reserved_qty",
        #     "fieldtype": "int",
        #     "width": 110,
        # },
        # {
        #     "label": "%Available",
        #     "fieldname": "total_qty",
        #     "fieldtype": "int",
        #     "width": 110,
        #     "disable_total": True
        # },
        # {
        #     "label": "Button",
        #     "fieldname": "button",
        #     "fieldtype": "Data",
        #     "width": 110,
        # },
    ]
    return columns


def get_data(filters):
    query = f"""
		SELECT
			1 AS `count`,
            soi.name as `soi_name`,
            soi.item_name as `item_name`,
            soi.reserved_qty as `reserved_status`,
            b.sales_order_reserved_qty as `sales_order_reserved_qty`,
			soi.name_of_brand AS `brand`,
			so.name AS `sales_order`,
            IF((b.actual_qty / (soi.qty - soi.delivered_qty)) * 100 > 110, 110, IF((b.actual_qty / (soi.qty - soi.delivered_qty)) * 100 < 0, 0, (b.actual_qty / (soi.qty - soi.delivered_qty)) * 100)) as `total_qty`,
			so.customer AS `customer`,
			soi.item_code AS `item_code`,
			b.warehouse AS `warehouse`,
			soi.qty AS `ordered_qty`,
			soi.delivered_qty AS `delivered_qty`,
			(soi.qty - soi.delivered_qty) AS `pending_qty`,
			b.actual_qty - b.sales_order_reserved_qty AS `actual_qty`,
            b.reserved_qty - b.sales_order_reserved_qty AS `need`,
            IF(b.reserved_qty - b.actual_qty <= 0, 0, b.reserved_qty - b.actual_qty) as `fullfill_so`,
            IF((soi.qty - soi.delivered_qty) - b.actual_qty <= 0, 0, (soi.qty - soi.delivered_qty) - b.actual_qty) as `fullfill_cu`,
			b.actual_qty - (soi.qty - soi.delivered_qty) AS `difference`,
			IF(b.actual_qty - (soi.qty - soi.delivered_qty) >= 0, 'Yes', 'No') AS `deliverable`,
			(SELECT b.actual_qty FROM `tabBin` AS b WHERE b.item_code = soi.item_code AND b.warehouse = 'Plain - RAPL') AS `Plain`,
			IF(b.actual_qty - (soi.qty - soi.delivered_qty) + (SELECT b.actual_qty FROM `tabBin` AS b WHERE b.item_code = soi.item_code AND b.warehouse = 'Plain - RAPL') >= 0, 'Yes', 'No') AS `IF Plain Used`
		FROM
			`tabSales Order` so
		JOIN
			`tabSales Order Item` soi ON soi.parent = so.name
		LEFT JOIN
			`tabBin` AS b ON b.item_code = soi.item_code AND b.warehouse = soi.warehouse
		WHERE
			so.status NOT IN ('Stopped', 'Closed', 'On Hold')
			AND so.docstatus = 1
			AND (soi.qty - soi.delivered_qty) > 0
		GROUP BY soi.name
		ORDER BY `difference`, so.transaction_date ASC, soi.item_code ASC;
    """
    result = frappe.db.sql(query, as_dict=True)
    for item in result:
        item[
            "button"
        ] = f"""
        <button type='button' warehouse = "{str(item['warehouse'])}" item_code = "{item['item_code']}" sales_order_reserved_qty = "{item['sales_order_reserved_qty']}" soi_name = "{item['soi_name']}" reserved_status = "{item['reserved_status']}" pending_qty = "{item['pending_qty']}"
            onClick='frappe.call({{
                method: "raplbaddi.salesrapl.report.sales_order_dispatchable.sales_order_dispatchable.reserve",
                args: {{
                    warehouse: this.getAttribute("warehouse"),
                    item_code: this.getAttribute("item_code"),
                    sales_order_reserved_qty: this.getAttribute("sales_order_reserved_qty"),
                    soi_name: this.getAttribute("soi_name"),
                    reserved_status: this.getAttribute("reserved_status"),
                    pending_qty: this.getAttribute("pending_qty")
                }},
                callback: function(r){{
                    frappe.throw(r);
                }}
            }})'>Reserve/Unreserve</button>
        """
    print(result)
    return result


@frappe.whitelist()
def execute(filters=None):
    columns, data = [], []
    return columns, data


def reserve(
    warehouse,
    item_code,
    sales_order_reserved_qty,
    soi_name,
    reserved_status,
    pending_qty,
):
    from erpnext.stock.stock_balance import update_bin_qty

    if float(reserved_status) == 1:
        frappe.db.sql(
            f"""
            UPDATE `tabSales Order Item` AS soi
            SET soi.reserved_qty = 0
            WHERE soi.name = '{soi_name}'
            """
        )
        res = float(sales_order_reserved_qty) - float(pending_qty)
        update_bin_qty(item_code, warehouse, {"sales_order_reserved_qty": res})
    else:
        frappe.db.sql(
            f"""
            UPDATE `tabSales Order Item` AS soi
            SET soi.reserved_qty = 1
            WHERE soi.name = '{soi_name}'
            """
        )
        res = float(sales_order_reserved_qty) + float(pending_qty)
        update_bin_qty(item_code, warehouse, {"sales_order_reserved_qty": res})


def get_conditions(filters):
    conditions = "1"
    if filters and filters.get("sales_person"):
        sales_person = filters.get("sales_person")
        conditions += f" AND dsr.sales_person = '{sales_person}'"
    if filters and filters.get("start_date"):
        start_date = filters.get("start_date")
        conditions += f" AND dsr.date >= '{start_date}'"
    if filters and filters.get("end_date"):
        end_date = filters.get("end_date")
        conditions += f" AND dsr.date <= '{end_date}'"
    if filters and filters.get("payment_status"):
        payment_status = filters.get("payment_status")
        conditions += f" AND status = '{payment_status}'"
    if filters and filters.get("payment_audited"):
        payment_audited = filters.get("payment_audited")
        if payment_audited == "Yes":
            print(payment_audited)
            conditions += f" AND payment_audited = '1'"
        elif payment_audited == "No":
            print(payment_audited)
            conditions += f" AND payment_audited = '0'"
        else:
            conditions += f" AND 1"
            print(payment_audited)
    return conditions


def get_group(filters):
    ret = "GROUP BY "
    if filters and filters.get("group_by_expense_type"):
        ret += "dse.type"
    else:
        ret = ""
    return ret

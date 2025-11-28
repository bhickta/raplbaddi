# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe


# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)
    return columns, data

def short_branch(name):
    if not name:
        return ""

    mapping = {
        "real appliances private limited": "RAPL",
        "red star unit 2": "RSU2"
    }

    return mapping.get(name.lower(), name)

def get_columns():
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Qty"), "fieldname": "qty", "fieldtype": "Int", "width": 90},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 120},
        {"label": _("Rate"), "fieldname": "rate", "fieldtype": "Currency", "width": 80},
        {"label": _("Tax %"), "fieldname": "custom_tax_rate", "fieldtype": "Float", "width": 90},
        {"label": _("Supplier"), "fieldname": "supplier_name", "fieldtype": "Link", "options": "Supplier", "width": 250},
        {"label": _("Item Group"), "fieldname": "item_group", "fieldtype": "Link", "options": "Item Group", "width": 150},
        {"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 100},
        {"label": _("Posting Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 120},
    ]


def get_data(filters):
    conditions = []
    params = {
        "from_date": filters.get("from_date"),
        "to_date": filters.get("to_date"),
    }

    # Mandatory date range
    if filters.get("from_date"):
        conditions.append("pr.posting_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("pr.posting_date <= %(to_date)s")

    # Filters
    if filters.get("item_code"):
        conditions.append("pri.item_code = %(item_code)s")
        params["item_code"] = filters.get("item_code")

    if filters.get("supplier"):
        conditions.append("pr.supplier = %(supplier)s")
        params["supplier"] = filters.get("supplier")

    if filters.get("item_group"):
        conditions.append("i.item_group = %(item_group)s")
        params["item_group"] = filters.get("item_group")

    where_clause = " AND " + " AND ".join(conditions) if conditions else ""

    sql = """
        SELECT
            pri.item_code,
            pri.qty,
            pri.warehouse,
            pri.rate,
            pr.custom_tax_rate,
            pr.supplier_name,
            i.item_group,
            pr.branch,
            pr.posting_date
        FROM
            `tabPurchase Receipt Item` pri
        INNER JOIN
            `tabPurchase Receipt` pr ON pr.name = pri.parent
        INNER JOIN
            `tabItem` i ON i.name = pri.item_code
        WHERE
            pr.docstatus = 1
            AND pri.qty > 0
            {where_clause}
        ORDER BY
            pr.posting_date DESC, pri.item_code
    """.format(where_clause=where_clause)

    data = frappe.db.sql(sql, params, as_dict=1)
    for d in data:
        d["branch"] = short_branch(d.get("branch"))

    return data
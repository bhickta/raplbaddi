# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt
import frappe

from frappe.core.doctype.user_permission.user_permission import get_user_permissions
from raplbaddi.datarapl.doctype.report_full_access_users.report_full_access_users import get_wildcard_users

def get_groups(user):
    user_permissions = get_user_permissions(user=user)
    allowed_groups = [groups['doc'] for groups in user_permissions.get('Customer Group', [])]
    return allowed_groups

def permissions(filters):
    user = frappe.session.user
    if filters.get('sales_person') in get_groups(user) or user in get_wildcard_users():
        return True
    else:
        return False

def execute(filters=None):
    columns, data = [], []
    if permissions(filters):
        data = get_data(filters)
        return get_columns(filters), data
    else:
        return None

def get_data(filters):
    query = f"""
        SELECT DISTINCT
            dn.name as dn,
            cu.name as customer,
            cu.customer_name as customer_name,
            dn.posting_date as posting_date,
            dn.total_qty as total_qty,
            dni.uom as uom,
            cu.customer_group as customer_group,
            GROUP_CONCAT(DISTINCT dni.item_name) as items
        FROM
            `tabDelivery Note` as dn
            LEFT JOIN `tabCustomer` as cu ON dn.customer = cu.name
            LEFT JOIN `tabDelivery Note Item` as dni ON dni.parent = dn.name
        WHERE {get_conditions(filters)}
        GROUP BY
            dn.name
        ORDER BY
            dn.posting_date DESC, dn.posting_time DESC
    """
    result = frappe.db.sql(query, as_dict=True)
    return result

def get_columns(filters):
    columns = [
        {"label": "Name", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 250},
        {"label": "Delivery Note", "fieldname": "dn", "fieldtype": "Link", "options": "Delivery Note", "width": 150},
        {"label": "Delivery Date", "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
        {"label": "Quantity", "fieldname": "total_qty", "fieldtype": "Int", "width": 50},
        {"label": "Unit", "fieldname": "uom", "fieldtype": "Data", "width": 50},
        {"label": "Name", "fieldname": "items", "fieldtype": "Data", "width": 150},
        {"label": "Salesman", "fieldname": "customer_group", "fieldtype": "Data", "width": 50},
    ]
    return columns

def get_conditions(filters):
    conditions = "dn.posting_date >= '2023-08-19' AND dn.docstatus = 1"
    if filters and filters.get("from_date"):
        from_date = filters.get("from_date")
        conditions += f" AND dn.posting_date >= '{from_date}'"
    if filters and filters.get("to_date"):
        to_date = filters.get("to_date")
        conditions += f" AND dn.posting_date <= '{to_date}'"
    if filters and filters.get("sales_person"):
        sales_person = filters.get("sales_person")
        conditions += f" AND cu.customer_group = '{sales_person}'"
    return conditions
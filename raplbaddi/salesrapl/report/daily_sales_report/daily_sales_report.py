# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.core.doctype.user_permission.user_permission import get_user_permissions
from raplbaddi.datarapl.doctype.report_full_access_users.report_full_access_users import get_wildcard_users

def get_groups(user):
    user_permissions = get_user_permissions(user=user)
    allowed_groups = [groups['doc'] for groups in user_permissions.get('Sales Person', [])]
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

def get_columns(filters):
    columns = [
        {
            "label": "Link",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Daily Sales Report By Admin", 
            "width": 100
        },
        {
            "label": "Start Reading",
            "fieldname": "start_reading",
            "fieldtype": "Int", 
            "width": 100, 
            "disable_total": True
        },
        {
            "label": "KM Travelled", 
            "fieldname": "km_travelled",
            "fieldtype": "Int", 
            "width": 100
        },
        {
            "label": "End Reading", 
            "fieldname": "end_reading",
            "fieldtype": "Int", 
            "disable_total": 1, 
            "width": 100, 
            "disable_total": True
        },
        {
            "label": "Date", 
            "fieldname": "date", 
            "fieldtype": "Date", 
            "width": 100
        },
        {
            "label": "Type", 
            "fieldname": "type", 
            "fieldtype": "Data", 
            "width": 180
        },
        {
            "label": "Amount", 
            "fieldname": "amount",
            "fieldtype": "Currency", 
            "width": 150
        },
    ]
    return columns


def get_amount(filters):
    if filters and filters.get("group_by_expense_type"):
        return 'SUM(dse.amount)'
    else:
        return 'dse.amount'


def get_data(filters):
    query = f"""
    SELECT DISTINCT
        dsr.name, dsr.date, dse.type, {get_amount(filters)} as amount, dsr.amount_for_travel, dsr.payment_audited, dsr.start_reading, dsr.end_reading, dsr.km_travelled
    FROM
        `tabDaily Sales Report By Admin` as dsr
        LEFT JOIN
        `tabDaily Sales Expenses By Admin` as dse ON dse.parent = dsr.name
    WHERE
        {get_conditions(filters)} and dsr.docstatus = 1
    {get_group(filters)}
    """
    result = frappe.db.sql(query, as_dict=True)
    unique_data = {}
    for item in result:
        date = item['date']
        amount = item.pop('amount_for_travel')
        start_reading = item.pop('start_reading')
        km_travelled = item.pop('km_travelled')
        end_reading = item.pop('end_reading')
        name = item.get('name')
        if date not in unique_data:
            unique_data[date] = [amount, name,
                                 start_reading, end_reading, km_travelled]

    amount_append = []
    for date, data in unique_data.items():
        d = {
            "date": date,
            "type": "Travel",
            "amount": data[0],
            "name": data[1],
            "start_reading": data[2],
            "end_reading": data[3],
            "km_travelled": data[4],
        }
        amount_append.append(d)
    result.extend(amount_append)
    return result


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
    if filters and filters.get("payment_audited"):
        payment_audited = filters.get("payment_audited")
        if payment_audited == 'Yes':
            print(payment_audited)
            conditions += f" AND payment_audited = '1'"
        elif payment_audited == 'No':
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

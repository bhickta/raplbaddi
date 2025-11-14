# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    return get_columns(filters), data


def get_data(filters):
    query = f"""
        SELECT
            parent,
            parameter,
            remark,
            capacity,
            brand_name,
            model_name,
            fault
        FROM
            `tabItem Testing Parameters` AS itp
        JOIN
            `tabSerial Number Geyser` AS sng ON sng.name = itp.parent
        WHERE
            fault = 1 AND {get_conditions(filters)}
        ORDER BY sng.name
    """

    result = frappe.db.sql(query, as_dict=True)
    return result


def get_columns(filters):
    columns = [
        {"label": "Serial Number", "fieldname": "parent", "fieldtype": "Link", "options": "Serial Number Geyser", "width": 150},
        {"label": "Parameter", "fieldname": "parameter", "fieldtype": "Data", "width": 150},
        {"label": "Brand", "fieldname": "brand_name", "fieldtype": "Data", "width": 150},
        {"label": "Model", "fieldname": "model_name", "fieldtype": "Data", "width": 150},
        {"label": "Capacity", "fieldname": "capacity", "fieldtype": "Data", "width": 150},
        {"label": "Remark", "fieldname": "remark", "fieldtype": "Data", "width": 150},
        {"label": "Have Fault ?", "fieldname": "fault", "fieldtype": "Int", "width": 150},
    ]
    return columns

def get_conditions(filters):
    conditions = "1=1"
    # if filters and filters.get("item"):
    #     item = filters.get("item")
    #     conditions += f" AND item='{item}'"
    if filters and filters.get("brand_name"):
        brand_name = filters.get("brand_name")
        conditions += f" AND brand_name='{brand_name}'"
    if filters and filters.get("start_date"):
        start_date = filters.get("start_date")
        conditions += f" AND date_of_production >= '{start_date}'"
    if filters and filters.get("end_date"):
        end_date = filters.get("end_date")
        conditions += f" AND date_of_production <= '{end_date}'"
    # if filters and filters.get("serial_number"):
    #     serial_number = filters.get("serial_number")
    #     conditions += f" AND ite.name = '{serial_number}'"
    return conditions

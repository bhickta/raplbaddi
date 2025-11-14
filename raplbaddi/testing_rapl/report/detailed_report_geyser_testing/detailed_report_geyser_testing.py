# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    return getColumns(filters), data

def get_data(filters):
    query = f"""
        SELECT ite.date_of_production, ite.brand_name, COUNT(*) AS frequency, itp.parameter, GROUP_CONCAT(ite.name SEPARATOR ', ') AS items, GROUP_CONCAT(itp.remark SEPARATOR ', ') AS remark
        FROM `tabItem Testing Entry` AS ite
        JOIN `tabItem Testing Parameters` AS itp ON itp.parent = ite.name
        WHERE itp.fault = 1 AND {get_conditions(filters)}
        GROUP BY itp.parameter
        ORDER BY frequency DESC
    """

    result = frappe.db.sql(query, as_dict=True)
    return result


def getColumns(filters):
    columns = [
        {"label": "Parameter", "fieldname": "parameter", "fieldtype": "Data", "width": 150},
        {"label": "Frequency", "fieldname": "frequency", "fieldtype": "Int", "width": 150},
    ]
    # if filters and filters.get("brand_name"):
    #     add = [
    #         {"label": "Brand Name", "fieldname": "brand_name", "fieldtype": "Data", "width": 150}
    #     ]
    #     columns.extend(add)
    # if filters and filters.get("serial_number"):
    #     add = [
    #         {"label": "Items", "fieldname": "items", "fieldtype": "Link", "width": 150, "options": "Item Testing Entry"}
    #     ]
    #     columns.extend(add)
    # else:
    #     add = [
    #         {"label": "Items", "fieldname": "items", "fieldtype": "Text", "width": 150,},
    #     ]
    #     columns.extend(add)

    return columns

def get_conditions(filters):
    conditions = "1=1"
    if filters and filters.get("item"):
        item = filters.get("item")
        conditions += f" AND item='{item}'"
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

# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    return get_columns(filters), data


def get_data(filters):
    query = f"""
    SELECT * FROM `tabDaily Production Entry` WHERE {get_conditions(filters)}
    """
    result = frappe.db.sql(query, as_dict=True)
    return result


def get_columns(filters):
    columns = []
    common = [
        {"label": "Date of Production", "fieldtype": "Date", "width": 150},
        {"label": "Item", "fieldtype": "Data", "width": 150},
        {"label": "Total Quantity", "fieldtype": "Int", "width": 150},
    ]
    item = filters.get("item")
    if item == "Geyser":
        add = [
            {"label": "Model Name", "fieldtype": "Data", "width": 150},
            {"label": "Brand Name", "fieldtype": "Data", "width": 150},
            {"label": "Capacity", "fieldtype": "Data", "width": 150},
        ]
        columns.extend(common)
        columns.extend(add)
    elif item == "Element":
        add = [
            {"label": "Element Type Name", "fieldtype": "Data", "width": 150},
        ]
        columns.extend(common)
        columns.extend(add)
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
    if filters and filters.get("item") == "Geyser" and filters.get("group_by_brand_model_capacity")
        conditions += f" GROUP BY item, brand_name, model_name, capacity"
    return conditions

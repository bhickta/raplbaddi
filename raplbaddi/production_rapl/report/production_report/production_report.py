# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    return get_columns(filters), data

# def get_message(filters):
#     query = f"""
#     SELECT SUM(manpower) as Manpower, date_of_production, item, production_line as Line FROM `tabDaily Work Force and Line` as dwl WHERE {get_conditions(filters)} GROUP BY production_line 
#     """
#     result = frappe.db.sql(query, as_dict=True)
#     messages = []
#     for entry in result:
#         res = " had ".join([f"{k}: {entry[k]}" for k in ['Line', 'Manpower'] if k in entry])
#         messages.append(res)
#     return " ;  ".join(messages)


def get_data(filters):
    query = f"""
    SELECT * FROM `tabProduction Entry`as pe WHERE {get_conditions(filters)}
    """
    result = frappe.db.sql(query, as_dict=True)
    return result


def get_columns(filters):
    columns = []
    common = [
        {"label": "Date of Production", "fieldname": "date_of_production", "fieldtype": "Date", "width": 150},
        {"label": "Line", "fieldname": "production_line", "fieldtype": "Data", "width": 50},
        {"label": "Workforce", "fieldname": "manpower", "fieldtype": "Data", "width": 50},
        {"label": "Item", "fieldtype": "Data", "width": 80},
    ]
    total = [
        {"label": "Quantity", "fieldname": "total_quantity", "fieldtype": "Int", "width": 140},
    ]
    item = filters.get("item")
    if item == "Geyser":
        add = [
            {"label": "Litre", "fieldname": "capacity", "fieldtype": "Data", "width": 150},
            {"label": "Model Name", "fieldtype": "Data", "width": 150},
            {"label": "Brand Name", "fieldtype": "Data", "width": 150},
        ]
        columns.extend(common)
        columns.extend(add)
        columns.extend(total)
    elif item == "Element":
        add = [
            {"label": "Element Type Name", "fieldtype": "Data", "width": 150},
        ]
        columns.extend(common)
        columns.extend(add)
        columns.extend(total)
    return columns


def get_conditions(filters):
    conditions = "pe.docstatus = 1"
    if filters and filters.get("item"):
        item = filters.get("item")
        conditions += f" AND item='{item}'"
    if filters and filters.get("brand_name"):
        brand_name = filters.get("brand_name")
        conditions += f" AND brand_name='{brand_name}'"
    if filters and filters.get("geyser_model"):
        geyser_model = filters.get("geyser_model")
        conditions += f" AND model_name='{geyser_model}'"
    if filters and filters.get("capacity"):
        capacity = filters.get("capacity")
        conditions += f" AND capacity='{capacity}'"
    if filters and filters.get("start_date"):
        start_date = filters.get("start_date")
        conditions += f" AND date_of_production >= '{start_date}'"
    if filters and filters.get("end_date"):
        end_date = filters.get("end_date")
        conditions += f" AND date_of_production <= '{end_date}'"
    if filters and filters.get("group_by_item_model_capacity_brand") and filters.get("item") == "Geyser":
        conditions += f" GROUP BY item, brand_name, model_name, capacity"
    return conditions

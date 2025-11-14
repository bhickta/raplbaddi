# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt
import frappe

def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    return get_columns(filters), data, get_message(filters, data)

def get_message(filters, data):
    sum1, sum2, sum3 = (0, 0, 0)
    for d in data:
        if d['production_line'] == '1':
            sum1 += d['total_quantity']
        if d['production_line'] == '2':
            sum2 += d['total_quantity']
        if d['production_line'] == '3':
            sum3 += d['total_quantity']
    ret = f"""
    <h3 style="display: inline;">
        <li>Line One = {sum1}</li>
        <li>Line Two= {sum2}</li>
        <li>Line Three= {sum3}</li>
    </h3>
    """
    return ret

def get_data(filters):
    query = f"""
    SELECT
        date_of_production,
        production_line,
        manpower,
        item
        {get_total_quantity(filters)} as total_quantity,
        capacity,
        brand_name,
        model_name,
        element_type_name
    FROM
        `tabProduction Entry`as pe
    WHERE
        {get_conditions(filters)}
    """
    result = frappe.db.sql(query, as_dict=True)
    return result

def get_total_quantity(filters):
    if filters and filters.get("group_by_item_model_capacity_brand"):
        return f", SUM(total_quantity)"
    else:
        return f", total_quantity"


def get_columns(filters):
    columns = []
    common = [
        {"label": "Date of Production", "fieldname": "date_of_production", "fieldtype": "Date", "width": 150},
        {"label": "Line", "fieldname": "production_line", "fieldtype": "Data", "width": 50},
        {"label": "Workforce", "fieldname": "manpower", "fieldtype": "Data", "width": 50},
        {"label": "Item", "fieldname": "item", "fieldtype": "Data", "width": 80},
    ]
    total = [
        {"label": "Quantity", "fieldname": "total_quantity", "fieldtype": "Int", "width": 140},
    ]
    item = filters.get("item")
    if item == "Geyser":
        add = [
            {"label": "Litre", "fieldname": "capacity", "fieldtype": "Data", "width": 150},
            {"label": "Model Name", "fieldname": "model_name", "fieldtype": "Data", "width": 150},
            {"label": "Brand Name", "fieldname": "brand_name", "fieldtype": "Data", "width": 150},
        ]
        columns.extend(common)
        columns.extend(add)
        columns.extend(total)
    elif item == "Element":
        add = [
            {"label": "Element Type Name", "fieldname": "element_type_name", "fieldtype": "Data", "width": 150},
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

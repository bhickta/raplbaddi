# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt
import frappe


def execute(filters=None):
    columns, data = [], []
    data = get_data(filters)
    return (
        get_columns(filters),
        data,
    )


def get_data(filters):
    query = f"""
		SELECT
			gpe.date_of_production, gpe.production_line,
            gpe.workforce, gpet.item_name, gpet.brand, i.capacity, i.geyser_model {get_total_quantity(filters)}
		FROM
			`tabGeyser Production Entry` as gpe
			LEFT JOIN
				`tabGeyser Production Entry Table` as gpet
					ON gpet.parent = gpe.name
			LEFT JOIN
				`tabItem` as i
					ON gpet.item = i.name
        WHERE
            {get_conditions(filters)}
    """
    result = frappe.db.sql(query, as_dict=True)
    return result


def get_total_quantity(filters):
    if filters and filters.get("group_by_item_model_capacity_brand"):
        return f", SUM(gpet.qty) as qty"
    else:
        return f", gpet.qty"


def get_columns(filters):
    columns = []
    common = [
        {
            "label": "Date of Production",
            "fieldname": "date_of_production",
            "fieldtype": "Date",
            "width": 150,
        },
        {"label": "Name", "fieldname": "item_name", "fieldtype": "Data", "width": 150},
        {
            "label": "Line",
            "fieldname": "production_line",
            "fieldtype": "Data",
            "width": 50,
        },
        {
            "label": "Workforce",
            "fieldname": "workforce",
            "fieldtype": "Data",
            "width": 50,
            "disable_total": True,
        },
    ]
    total = [
        {"label": "Quantity", "fieldname": "qty", "fieldtype": "Int", "width": 140},
    ]
    add = [
        {
            "label": "Litre",
            "fieldname": "capacity",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": "Model Name",
            "fieldname": "geyser_model",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": "Brand Name",
            "fieldname": "brand",
            "fieldtype": "Data",
            "width": 150,
        },
    ]
    columns.extend(common)
    columns.extend(add)
    columns.extend(total)
    return columns


def get_conditions(filters):
    conditions = "gpe.docstatus = 1"
    if filters and filters.get("start_date"):
        start_date = filters.get("start_date")
        conditions += f" AND gpe.date_of_production >= '{start_date}'"
    if filters and filters.get("end_date"):
        end_date = filters.get("end_date")
        conditions += f" AND gpe.date_of_production <= '{end_date}'"

    item_group = filters.get("item_group")
    if item_group:
        if len(item_group) > 1:
            conditions += f" AND i.item_group in {tuple(item_group)}"
        else:
            conditions += f" AND i.item_group = '{item_group[0]}'"

    return conditions

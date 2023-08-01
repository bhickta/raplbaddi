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
			gpe.date_of_production, gpe.production_line as production_line, gpe.date_of_production, i.geyser_capacity as capacity, i.geyser_model as model, gpet.qty as total
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
    ;
    """
    result = frappe.db.sql(query, as_dict=True)
    return result


def get_columns(filters):
    columns = [
        {"label": "Date", "fieldtype": "Date",
            "width": 150, "fieldname": "date_of_production"},
        {"label": "Model Name", "fieldtype": "Data",
            "width": 150, "fieldname": "model"},
        {"label": "Capacity", "fieldtype": "Data",
            "width": 80, "fieldname": "capacity"},
        {"label": "Total Quantity", "fieldtype": "Int",
            "width": 140, "fieldname": "total"},
        {"label": "Production Line", "fieldtype": "Data",
            "width": 140, "fieldname": "production_line"},
    ]
    return columns


def get_month_number(month):
    month = month.lower()
    if month == "jan":
        return 1
    elif month == "feb":
        return 2
    elif month == "mar":
        return 3
    elif month == "apr":
        return 4
    elif month == "may":
        return 5
    elif month == "jun":
        return 6
    elif month == "jul":
        return 7
    elif month == "aug":
        return 8
    elif month == "sep":
        return 9
    elif month == "oct":
        return 10
    elif month == "nov":
        return 11
    elif month == "dec":
        return 12
    else:
        return None


def get_conditions(filters):
    conditions = "1=1"
    if filters and filters.get("item"):
        item = filters.get("item")
        conditions += f" AND item = '{item}'"
    if filters and filters.get("month"):
        month = get_month_number(filters.get("month"))
        conditions += f" AND MONTH(date_of_production) = {month}"
    conditions += " AND gpe.docstatus = 1"
    return conditions

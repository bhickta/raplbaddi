# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
# Copyright (c) 2025, Nishant Bhickta
# For license information, please see license.txt

# Copyright (c) 2025, Nishant Bhickta and contributors
# For license information, please see license.txt

# import frappe
import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def extract_year_month(serial_no):
    if not serial_no:
        return "NA", "NA"

    s = serial_no.strip().upper()
	# Example: F3XXXX
    if len(s) >= 2 and s[0].isalpha() and s[1].isdigit():
        month_letter = s[0]
        year_digit = s[1]

        month_map = {
            "A": "01", "B": "02", "C": "03", "D": "04",
            "E": "05", "F": "06", "G": "07", "H": "08",
            "I": "09", "J": "10", "K": "11", "L": "12"
        }

        if month_letter in month_map:
            month = int(month_map[month_letter])   # Convert "06" → 6
            year = 2020 + int(year_digit)          # "3" → 2023
            return year, month
	RS4K → 4 → 2024, K → 11 (November)
    # ----------------------------------------------------
    if serial.startswith("RS") and len(serial) >= 4:
        year_digit = serial[2]        # "4"
        month_letter = serial[3]      # "K"

        if year_digit.isdigit():
            year = "202" + year_digit  # → 2024
        else:
            year = None

        month = month_map.get(month_letter, None)

        return year, month

    # ----------------------------------------------------
    # Numeric only: YMMxxxxx  (4120590 → 2024, 12)
    # ----------------------------------------------------
    if s.isdigit() and len(s) >= 3:
        try:
            year = 2000 + int(s[0])          # "4" → 2024
            month = int(s[1:3])              # "12" → December
            if 1 <= month <= 12:
                return year, month
        except:
            pass

    # ----------------------------------------------------
    # RGS format: RGS + YYMM  (RGS2207 → 2022, July)
    # ----------------------------------------------------
    if s.startswith("RGS") and len(s) >= 7:
        try:
            year = 2000 + int(s[3:5])
            month = int(s[5:7])
            if 1 <= month <= 12:
                return year, month
        except:
            pass
from datetime import datetime

def get_manufacturing_date(year, month):
    """Convert extracted year + month → proper date object (1st of month)."""
    if not year or not month:
        return None
    try:
        return datetime.strptime(f"{year}-{int(month):02d}-01", "%Y-%m-%d")
    except:
        return None

def get_date_difference(manufacturing_date, complaint_date):
    """Return difference in days."""
    if not manufacturing_date or not complaint_date:
        return None
    try:
        return (complaint_date - manufacturing_date).days
    except:
        return None


def get_columns():
    return [
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
        {"label": _("Brand Name"), "fieldname": "brand_name", "fieldtype": "Data", "width": 150},
        {"label": _("Issue Type"), "fieldname": "issue_type", "fieldtype": "Data", "width": 150},
        {"label": _("Sub Issue"), "fieldname": "sub_issue", "fieldtype": "Data", "width": 250},
        {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": _("Geyser Capacity"), "fieldname": "geyser_capacity", "fieldtype": "Data", "width": 140},
        {"label": _("Geyser Model"), "fieldname": "geyser_model", "fieldtype": "Data", "width": 150},
        {"label": _("Serial No"), "fieldname": "serial_no", "fieldtype": "Data", "width": 120},
        {"label": _("Year"), "fieldname": "year", "fieldtype": "Int", "width": 80},
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Int", "width": 80},
        {"label": _("Creation Date"), "fieldname": "creation_date", "fieldtype": "Date", "width": 120},
        {"label": _("Sale Date"), "fieldname": "sale_date", "fieldtype": "Date", "width": 120},
        {"label": _("Mfg Date"), "fieldname": "mfg_date", "fieldtype": "Date", "width": 120},
        {"label": _("Age in Days"), "fieldname": "age_in_days", "fieldtype": "Int", "width": 120}
    ]

def get_data(filters):
    conditions = []
    values = {}

    if filters.get("status"):
        conditions.append("status = %(status)s")
        values["status"] = filters.get("status")

    if filters.get("brand_name"):
        conditions.append("brand_name = %(brand_name)s")
        values["brand_name"] = filters.get("brand_name")

    if filters.get("issue_type"):
        conditions.append("issue_type = %(issue_type)s")
        values["issue_type"] = filters.get("issue_type")

    if filters.get("sub_issue"):
        conditions.append("sub_issue = %(sub_issue)s")
        values["sub_issue"] = filters.get("sub_issue")

    if filters.get("state"):
        conditions.append("state = %(state)s")
        values["state"] = filters.get("state")

    if filters.get("geyser_capacity"):
        conditions.append("geyser_capacity = %(geyser_capacity)s")
        values["geyser_capacity"] = filters.get("geyser_capacity")

    if filters.get("geyser_model"):
        conditions.append("geyser_model = %(geyser_model)s")
        values["geyser_model"] = filters.get("geyser_model")

    condition_str = " and ".join(conditions)
    if condition_str:
        condition_str = " where " + condition_str

    query = f"""
        SELECT
            ir.status,
            ir.brand_name,
            iri.issue_type,
            IFNULL(iri.sub_issue , 'Not Specified') as sub_issue,
            ir.customer_address_state as state,
            ir.geyser_capacity,
            ir.model as geyser_model,
            ir.custom_serial_number as serial_no,
            ir.custom_creation_date as creation_date,
            ir.invoice_date as sale_date
        FROM tabIssueRapl AS ir
JOIN `tabIssueRapl Item` AS iri ON ir.name = iri.parent

{condition_str}
"""

    rows = frappe.db.sql(query, values, as_dict=True)

    # Add Year + Month extracted fields
    for r in rows:
        year, month = extract_year_month(r.serial_no) or (None, None)
        r.year = year
        r.month = month

    return rows

import frappe
from frappe import _
from datetime import datetime

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def extract_year_month(serial_no):
    if not serial_no:
        return None, None

    s = serial_no.strip().upper()

    # ----------------------------------------------------
    # Numeric only: YMMxxxxx  (4120590 → 2024, 12)
    # ----------------------------------------------------
    if s.isdigit() and len(s) >= 3:
        try:
            year = 2020 + int(s[0])          # "4" → 2024
            month = int(s[1:3])              # "12" → December
            if 1 <= month <= 12:
                return year, month
        except:
            pass

    # ----------------------------------------------------
    #  RGS format: RGS + YYMM  (RGS2207 → 2022, July)
    # ----------------------------------------------------
    if s.startswith("RGS") and len(s) >= 7:
        try:
            year = 2000 + int(s[3:5])
            month = int(s[5:7])
            if 1 <= month <= 12:
                return year, month
        except:
            pass
    
    

    # ----------------------------------------------------
    # RS format: RS + Y + CODE_LETTER  (RS4K6811 → 2024, 11)
    # ----------------------------------------------------
    if s.startswith("RS") and len(s) >= 4:
        try:
            year_digit = s[2]      # 4
            month_letter = s[3]    # K

            month_map = {
                "A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6,
                "G": 7, "H": 8, "I": 9, "J": 10, "K": 11, "L": 12
            }

            year = 2020 + int(year_digit)  
            month = month_map.get(month_letter)

            if month:
                return year, month
        except:
            pass
    
    # ----------------------------------------------------
    # F3XXXX type (Letter + Digit)
    #    F = June (06), 3 = 2023
    # ----------------------------------------------------
    month_map = {
        "A": 1, "B": 2, "C": 3, "D": 4,
        "E": 5, "F": 6, "G": 7, "H": 8,
        "I": 9, "J": 10, "K": 11, "L": 12
    }
    if len(s) >= 2 and s[0].isalpha() and s[1].isdigit():
        month_letter = s[0]
        year_digit = s[1]

        if month_letter in month_map:
            month = month_map[month_letter]
            year = 2020 + int(year_digit)  # 3 → 2023
            return year, month

    return None, None


def get_creation_to_mfg(mfg_date_str, creation_date_any):
    if not mfg_date_str or not creation_date_any:
        return None
    try:
        mfg_date = datetime.strptime(mfg_date_str, "%Y-%m-%d").date()
        if isinstance(creation_date_any, str):
            creation_date = datetime.strptime(creation_date_any, "%Y-%m-%d").date()
        else:
            creation_date = creation_date_any  # already date object
        return max((creation_date - mfg_date).days, 0)
    except:
        return None

def get_sale_to_mfg(mfg_date_str, sale_date_any):
    if not mfg_date_str or not sale_date_any:
        return None
    try:
        mfg_date = datetime.strptime(mfg_date_str, "%Y-%m-%d").date()
        if isinstance(sale_date_any, str):
            sale_date = datetime.strptime(sale_date_any, "%Y-%m-%d").date()
        else:
            sale_date = sale_date_any
        gap = (sale_date - mfg_date).days
        return max(gap, 0)  # negative na aaye
    except:
        return None

    
def get_columns():
    return [
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 80},
        {"label": _("Brand Name"), "fieldname": "brand_name", "fieldtype": "Data", "width": 120},
        {"label": _("Issue Type"), "fieldname": "issue_type", "fieldtype": "Data", "width": 120},
        {"label": _("Sub Issue"), "fieldname": "sub_issue", "fieldtype": "Data", "width": 150},
        {"label": _("State"), "fieldname": "state", "fieldtype": "Data", "width": 120},
        {"label": _("Geyser Capacity"), "fieldname": "geyser_capacity", "fieldtype": "Data", "width": 90},
        {"label": _("Geyser Model"), "fieldname": "geyser_model", "fieldtype": "Data", "width": 120},
        {"label": _("Serial No"), "fieldname": "serial_no", "fieldtype": "Data", "width": 100},
        {"label": _("Year"), "fieldname": "year", "fieldtype": "Int", "width": 80},
        {"label": _("Month"), "fieldname": "month", "fieldtype": "Int", "width": 80},
        {"label": _("Creation Date"), "fieldname": "creation_date", "fieldtype": "Date", "width": 120},
        {"label": _("Sale Date"), "fieldname": "sale_date", "fieldtype": "Date", "width": 120},{"label": _("Mfg Date"), "fieldname": "mfg_date", "fieldtype": "Date", "width": 150},
        {"label": _("Creation to Mfg (Days)"), "fieldname": "creation_to_mfg", "fieldtype": "Int", "width": 120},
        {"label": _("Sale to Mfg(Days)"), "fieldname": "sale_to_mfg", "fieldtype": "Int", "width": 120},
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
            IFNULL(ir.customer_address_state, 'Not Mentioned') as state,
            IFNULL(ir.geyser_capacity , 'Not Specified') as geyser_capacity,
            IFNULL(ir.model , 'Not Mentioned') as geyser_model,
            IFNULL(ir.custom_serial_number , 'Not Specified ') as serial_no,
            ir.custom_creation_date as creation_date,
            IFNULL(ir.invoice_date , '') as sale_date
            
        FROM tabIssueRapl AS ir
JOIN `tabIssueRapl Item` AS iri ON ir.name = iri.parent
{condition_str}
"""

    rows = frappe.db.sql(query, values, as_dict=True)

     # Add Year, Month and Combined Column
    # --------------------------------------
    rows = rows or []

    for r in rows:
        year, month = extract_year_month(r.get("serial_no") or "")


    # keep year/month fields too (optional)
        r["year"] = year
        r["month"] = month


    # put combined value into mfg_date as a valid Date (first day of that month)
        if year and month:
            r["mfg_date"] = f"{int(year):04d}-{str(month).zfill(2)}-01"
        else:
        # leave blank or set None so Date column stays empty
            r["mfg_date"] = None
                     
        if r["mfg_date"] and r.get("creation_date"):
            r["creation_to_mfg"] = get_creation_to_mfg(r["mfg_date"], r.get("creation_date")) or 0
        else:
            r["creation_to_mfg"] = 0

        if r["mfg_date"] and r.get("sale_date"):
            r["sale_to_mfg"] = get_sale_to_mfg(r["mfg_date"], r.get("sale_date")) or 0
        else:
            r["sale_to_mfg"] = 0
        r["year"]            = year if year is not None else "0"
        r["month"]           = month if month is not None else "0"
        
    return rows
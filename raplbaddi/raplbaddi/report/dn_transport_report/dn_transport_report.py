import frappe
from collections import defaultdict

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {"label": "Posting Date", "fieldname": "posting_date",
         "fieldtype": "Data", "width": 110},

        {"label": "Vehicle No", "fieldname": "vehicle_no",
         "fieldtype": "Data", "width": 130},

        {"label": "Customer Name(s)", "fieldname": "customer_name",
         "fieldtype": "Data", "width": 200},

        {"label": "Transporter Name(s)", "fieldname": "transporter_name",
         "fieldtype": "Data", "width": 180},

        {"label": "Dala?", "fieldname": "dala",
         "fieldtype": "Data", "width": 80},

        {"label": "Double Height?", "fieldname": "double_height",
         "fieldtype": "Data", "width": 120},

        {"label": "Total Qty", "fieldname": "total_qty",
         "fieldtype": "Float", "width": 120},

        {"label": "Total CBM", "fieldname": "total_cbm",
         "fieldtype": "Float", "width": 120},
    ]


def get_data(filters):

    # FETCH ALL DELIVERY NOTES
    dn_list = frappe.db.sql("""
        SELECT
            dn.name,
            dn.posting_date,
            dn.customer_name,
            dn.custom_vehicle_no,
            dn.transporter_name
        FROM `tabDelivery Note` dn
        WHERE dn.docstatus = 1
        ORDER BY dn.posting_date DESC
    """, as_dict=True)


    # GROUP STORAGE
    groups = defaultdict(lambda: {
        "customer_names": set(),
        "transporter_names": set(),
        "total_qty": 0,
        "total_cbm": 0,
        "dala": "No",
        "double_height": "No"
    })


    for dn in dn_list:

        # 🔥 FIXED GROUPING KEY — date converted to "YYYY-MM-DD"
        posting_date_str = dn.posting_date.strftime("%Y-%m-%d")
        vehicle = dn.custom_vehicle_no or "N/A"

        key = (posting_date_str, vehicle)
        group = groups[key]

        # ADD customer + transporter
        group["customer_names"].add(dn.customer_name or "N/A")
        group["transporter_names"].add(dn.transporter_name or "Not Available")

        # FETCH DN ITEMS
        items = frappe.db.sql("""
            SELECT item_code, qty
            FROM `tabDelivery Note Item`
            WHERE parent = %s
        """, dn.name, as_dict=True)

        for it in items:
            qty = it.qty or 0
            if qty <= 0:
                continue

            group["total_qty"] += qty

            cbm_vals = frappe.db.sql("""
                SELECT cbm_length, cbm_width, cbm_height
                FROM `tabItem`
                WHERE name = %s
            """, it.item_code, as_dict=True)

            if not cbm_vals:
                continue

            L = cbm_vals[0].cbm_length or 0
            W = cbm_vals[0].cbm_width or 0
            H = cbm_vals[0].cbm_height or 0

            cbm = (L/1000) * (W/1000) * (H/1000)
            group["total_cbm"] += cbm * qty


        # FETCH FREIGHT CHILD TABLE
        freight = frappe.db.sql("""
            SELECT type
            FROM `tabFreight Table`
            WHERE parent = %s
        """, dn.name, as_dict=True)

        for f in freight:
            if f.type == "Dala":
                group["dala"] = "Yes"
            if f.type == "Double Height":
                group["double_height"] = "Yes"



    # PREP FINAL RESULT
    result = []

    for (posting_date, vehicle_no), g in groups.items():
        result.append({
            "posting_date": posting_date,
            "vehicle_no": vehicle_no,
            "customer_name": ", ".join(g["customer_names"]),
            "transporter_name": ", ".join(g["transporter_names"]),
            "dala": g["dala"],
            "double_height": g["double_height"],
            "total_qty": g["total_qty"],
            "total_cbm": round(g["total_cbm"], 3)
        })

    return result

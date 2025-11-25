import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    return columns, data


def get_columns():
    return [
        {"label": "Delivery Note", "fieldname": "delivery_note",
         "fieldtype": "Link", "options": "Delivery Note", "width": 150},

        {"label": "Posting Date", "fieldname": "posting_date",
         "fieldtype": "Date", "width": 110},

        {"label": "Transporter Name", "fieldname": "transporter_name",
         "fieldtype": "Data", "width": 180},

        {"label": "Vehicle No", "fieldname": "vehicle_no",
         "fieldtype": "Data", "width": 130},

        {"label": "Load Type (Dala / Normal)", "fieldname": "load_type",
         "fieldtype": "Data", "width": 160},

        {"label": "Double Height?", "fieldname": "double_height",
         "fieldtype": "Data", "width": 130},

        {"label": "Total CBM", "fieldname": "total_cbm",
         "fieldtype": "Float", "width": 120},

        {"label": "Total Qty", "fieldname": "total_qty",
         "fieldtype": "Float", "width": 120},
    ]


def get_data(filters):

    # FETCH ALL DELIVERY NOTES
    dn_list = frappe.db.sql("""
        SELECT
            dn.name,
            dn.posting_date,
            dn.custom_vehicle_no,
            dn.transporter_name,
            dn.custom_dala,
            dn.custom_double_height
        FROM `tabDelivery Note` dn
        WHERE dn.docstatus = 1
        ORDER BY dn.posting_date DESC
    """, as_dict=True)

    result = []

    for dn in dn_list:

        # FETCH DN ITEMS
        items = frappe.db.sql("""
            SELECT item_code, qty
            FROM `tabDelivery Note Item`
            WHERE parent = %s
        """, dn.name, as_dict=True)

        total_qty = 0
        total_cbm = 0

        for it in items:

            qty = it.qty or 0
            if qty <= 0:
                continue     # ignore returns

            total_qty += qty

            # FETCH CBM FROM ITEM MASTER
            cbm_vals = frappe.db.sql("""
                SELECT 
                    cbm_length, cbm_width, cbm_height
                FROM `tabItem`
                WHERE name = %s
            """, it.item_code, as_dict=True)

            if not cbm_vals:
                continue

            L = cbm_vals[0].cbm_length or 0
            W = cbm_vals[0].cbm_width or 0
            H = cbm_vals[0].cbm_height or 0

            # MM → M Conversion → CBM
            cbm = (L / 1000) * (W / 1000) * (H / 1000)

            total_cbm += cbm * qty

        # --------------------
        # FINAL OUTPUT ROW (WITH FALLBACK VALUES)
        # --------------------
        result.append({
            "delivery_note": dn.name,
            "posting_date": dn.posting_date,

            # 🔥 fallback values added here
            "vehicle_no": dn.custom_vehicle_no or "N/A",
            "transporter_name": dn.transporter_name or "Not Available",

            "load_type": "Dala" if dn.custom_dala else "Normal",
            "double_height": "Yes" if dn.custom_double_height else "No",

            "total_qty": total_qty,
            "total_cbm": round(total_cbm, 3)
        })

    return result

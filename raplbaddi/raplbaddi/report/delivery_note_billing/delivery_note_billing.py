import frappe
from frappe.utils import flt
import math


def execute(filters=None):
    columns, data = get_columns(), get_data(filters)
    return columns, data


def get_columns():
    return [
        {
            "label": "Delivery Note",
            "fieldname": "dn",
            "fieldtype": "Link",
            "options": "Delivery Note",
            "width": 150,
        },
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150,
        },
        {
            "label": "Capacity",
            "fieldname": "capacity",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": "Billing Rule",
            "fieldname": "billing_rule",
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "label": "Total Qty",
            "fieldname": "total_qty",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": "Estimate Amount",
            "fieldname": "estimate_amount",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": "Base Rate",
            "fieldname": "base_rate",
            "fieldtype": "Currency",
            "width": 100,
        },
        {
            "label": "50%",
            "fieldname": "fifty_percent",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": "55%",
            "fieldname": "fifty_five_percent",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": "100%",
            "fieldname": "fifty_five_percent",
            "fieldtype": "Data",
            "width": 100,
        },
    ]


billing_rules = {
    "2 Round System (100% Paid)": {"50%": None, "55%": None, "100%": True},
    "25-30% Paid": {"50%": True, "55%": True, "100%": None},
    "UB-Extra": {"50%": True, "55%": True, "100%": False},
    "9% Extra": {"50%": None, "55%": None, "100%": False},
    "2 Round System (60/30)": {"50%": True, "55%": True, "100%": None},
    "WB": {"50%": True, "55%": True, "100%": None},
    "UB-Paid": {"50%": True, "55%": True, "100%": None},
    "GST Extra As Applicable": {"50%": None, "55%": None, "100%": False},
    "100% Paid": {"50%": None, "55%": None, "100%": True},
    "50% Paid": {"50%": True, "55%": True, "100%": None},
}


def get_data(filters):
    conditions = get_conditions(filters)

    dn_items = frappe.db.sql(
        """
        SELECT
            dn.name AS dn,
            dn.customer,
            dn.customer_name,
            i.capacity,
            dn.billing_rule,
            SUM(dni.qty) AS total_qty,
            SUM(dni.amount) AS estimate_amount,
            iwbr.rates * 1.18 AS base_rate
        FROM
            `tabDelivery Note` dn
        LEFT JOIN
            `tabDelivery Note Item` dni ON dni.parent = dn.name
        LEFT JOIN
            `tabItem` i ON dni.item_code = i.name
        LEFT JOIN
            `tabItemwise billing rates` iwbr ON iwbr.ltr = i.capacity
        WHERE
            {conditions}
        GROUP BY
            dn.name, i.capacity
        ORDER BY
            dn.name DESC, i.capacity DESC
    """.format(
            conditions=conditions
        ),
        as_dict=True,
    )

    data = []
    for row in dn_items:
        estimate_amount = flt(row.estimate_amount)
        base_rate = flt(row.base_rate)
        total_qty = flt(row.total_qty)

        # Calculating the values for 50%, 55%, etc.
        fifty_percent_value = calculate_percentage(
            base_rate, total_qty, estimate_amount, 0.50
        )
        fifty_five_percent_value = calculate_percentage(
            base_rate, total_qty, estimate_amount, 0.55
        )
        hundred_percent_value = calculate_percentage(
            base_rate, total_qty, estimate_amount, 1
        )

        data.append(
            {
                "dn": row.dn,
                "customer": row.customer,
                "customer_name": row.customer_name,
                "capacity": row.capacity,
                "billing_rule": row.billing_rule,
                "total_qty": total_qty,
                "estimate_amount": estimate_amount,
                "base_rate": base_rate,
                "fifty_percent": get_display_value(
                    row.billing_rule, "50%", fifty_percent_value
                ),
                "fifty_five_percent": get_display_value(
                    row.billing_rule, "55%", fifty_five_percent_value
                ),
                "hundred_percent": get_display_value(
                    row.billing_rule, "100%", hundred_percent_value
                ),
            }
        )
    return data


def get_display_value(billing_rule, percentage, calculated_value):
    # Check if the billing rule exists in the dictionary
    rule = billing_rules.get(billing_rule)
    if not rule:
        return "N/A"

    # Check the status for the specified percentage (e.g., "50%", "55%")
    status = rule.get(percentage)

    # Return "N/A" if the status is None, or the calculated value if True/False
    if status is None:
        return "N/A"
    elif status:
        # Return the calculated value if the status is True
        return calculated_value
    else:
        # Return "N/A" if the status is explicitly False
        return "N/A"


def calculate_percentage(base_rate, total_qty, estimate_amount, percentage):
    if base_rate > 0:
        adjustment = flt(base_rate * total_qty - estimate_amount * percentage)
        return math.ceil(adjustment / base_rate) if adjustment >= 0 else 0
    else:
        return 0


def get_conditions(filters):
    conditions = []
    conditions.append("dn.docstatus = 1 and dn.is_return = 0")
    conditions.append("i.item_group = 'Geyser Unit'")
    return " AND ".join(conditions)

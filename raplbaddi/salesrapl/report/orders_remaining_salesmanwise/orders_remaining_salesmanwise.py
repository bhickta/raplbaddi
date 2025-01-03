import frappe
from frappe.core.doctype.user_permission.user_permission import get_user_permissions
import frappe.utils
from raplbaddi.datarapl.doctype.report_full_access_users.report_full_access_users import get_wildcard_users

def get_groups(user):
    user_permissions = get_user_permissions(user=user)
    allowed_groups = [groups['doc'] for groups in user_permissions.get('Sales Person', [])]
    return allowed_groups

def permissions(filters):
    user = frappe.session.user
    if filters.get('sales_person') in get_groups(user) or user in get_wildcard_users():
        return True
    else:
        return False

def execute(filters=None):
    columns, data = [], []
    if permissions(filters):
        data = process_data(filters)
        return get_columns(filters), data
    else:
        return None

def process_data(filters):
    # Fetch raw data
    sales_orders = fetch_sales_orders(filters)
    
    # Process data in Python
    processed_data = []
    for order in sales_orders:
        order_data = {
            'date': order.transaction_date,
            'sales_orders': format_sales_order_link(order.name),
            'salesman': order.sales_person,
            'customer_group': order.customer_group,
            'delivery_date': get_delivery_date(order),
            'customer': order.customer,
            'customer_name': order.customer_name,
            'brand': order.name_of_brand,
            'orders': order.qty,
            'delivered': order.delivered_qty,
            'remarks': order.conditions,
            'shipping_address': order.shipping_address,
        }
        processed_data.append(order_data)
    
    return processed_data

def fetch_sales_orders(filters):
    # Basic atomic query fetching only necessary fields
    query = f"""
        SELECT
            so.transaction_date,
            so.name,
            so.sales_person,
            so.delivery_date,
            so.customer AS customer,
            so.customer_name AS customer_name,
            so.total_qty qty,
            soi.delivered_qty,
            soi.name_of_brand,
            cu.customer_group,
            so.conditions,
            so.shipping_address
        FROM `tabSales Order` so
        JOIN `tabSales Order Item` soi ON soi.parent = so.name
        LEFT JOIN `tabCustomer` as cu ON cu.name = so.customer
        WHERE {get_conditions(filters)}
        AND so.docstatus = 1 AND soi.qty > soi.delivered_qty
        GROUP BY so.name
    """
    data = frappe.db.sql(query, as_dict=True)
    return frappe.db.sql(query, as_dict=True)

def get_delivery_date(order):
    if order.delivery_date == '2023-12-31' or order.delivery_date < frappe.utils.now_datetime().date():
        return 'Hold' if order.conditions == 'On Hold' else 'Current'
    return frappe.utils.formatdate(order.delivery_date, 'dd/MMM/YYYY')

def format_sales_order_link(order_name):
    return f'<a href="https://raplbaddi.com/app/sales-order/{order_name}">{order_name}</a>'

def calculate_percentage(order):
    actual_qty = frappe.db.get_value("Bin", {"item_code": order.name_of_brand}, "actual_qty") or 0
    required_qty = order.qty - order.delivered_qty
    if required_qty == 0:
        return 0
    percentage = (actual_qty / required_qty) * 100
    return min(max(int(percentage), 0), 100)

def calculate_shortage(order):
    actual_qty = frappe.db.get_value("Bin", {"item_code": order.name_of_brand}, "actual_qty") or 0
    required_qty = order.qty - order.delivered_qty
    shortage = required_qty - actual_qty
    return max(shortage, 0)

def get_columns(filters):
    return [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 250},
        {"label": "Sales Orders", "fieldname": "sales_orders", "fieldtype": "Data", "options": "Sales Order", "width": 150},
        {"label": "Order Date", "fieldname": "date", "fieldtype": "Date", "width": 100},
        {"label": "Delivery Date", "fieldname": "delivery_date", "fieldtype": "Data", "width": 100},
        {"label": "Orders", "fieldname": "orders", "fieldtype": "Int", "width": 50},
        {"label": "Delivered", "fieldname": "delivered", "fieldtype": "Int", "width": 50},
        {"label": "Brand", "fieldname": "brand", "fieldtype": "Data", "width": 50},
        {"label": "Shipping Address", "fieldname": "shipping_address", "fieldtype": "Data", "width": 150},
        {"label": "Salesman", "fieldname": "customer_group", "fieldtype": "HTML", "width": 50},
        {"label": "Remarks", "fieldname": "remarks", "fieldtype": "Data", "width": 150},
    ]

def get_conditions(filters):
    conditions = "so.status NOT IN ('Stopped', 'Closed')"
    if filters.get("from_date"):
        conditions += f" AND so.transaction_date >= '{filters['from_date']}'"
    if filters.get("to_date"):
        conditions += f" AND so.transaction_date <= '{filters['to_date']}'"
    if filters.get("sales_person"):
        conditions += f" AND cu.customer_group = '{filters['sales_person']}'"
    return conditions
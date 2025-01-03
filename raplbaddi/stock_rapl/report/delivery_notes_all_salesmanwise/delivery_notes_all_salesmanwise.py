# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt
import frappe
from frappe.core.doctype.user_permission.user_permission import get_user_permissions
from raplbaddi.datarapl.doctype.report_full_access_users.report_full_access_users import get_wildcard_users
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, CurDate, Max, DateDiff, CustomFunction
from pypika import Case
import datetime

def get_groups(user):
    user_permissions = get_user_permissions(user=user)
    allowed_groups = [groups['doc'] for groups in user_permissions.get('Customer Group', [])]
    return allowed_groups

def permissions(filters):
    user = frappe.session.user
    if filters.get('sales_person') in get_groups(user) or user in get_wildcard_users():
        return True
    if filters.get('sales_person') == 'All' and user in get_wildcard_users():
        return True
    else:
        return False

def execute(filters=None):
    columns, data = [], []
    if permissions(filters):
        data = join(filters)
        return get_columns(filters), data
    else:
        return None

def get_tally_data():
    td = DocType('Tally April to August 2023')
    tpn = DocType('Tally Party Name')
    tp = DocType('Tally Particular')
    i = DocType('Item')
    query = (frappe.qb
        .from_(td)
        .left_join(tpn).on(td.party_name == tpn.name)
        .left_join(tp).on(tp.name == td.particulars)
        .left_join(i).on(tp.item == i.name)
        .where(
            (td.date >= '2023-04-01') & (td.date <= '2023-08-28') &
            (td.transaction_type == 'Sales') &
            (i.item_group == 'Geyser Unit')
        )
        .select(
            Case()
                .when(td.transaction_type == 'Sales', td.quantity)
                .else_(-td.quantity)
            .as_('net_sales'),
            td.date.as_('date'),
            tpn.customer.as_('customer')
        )
        )
    
    result = query.run(as_dict=True)
    for r in result:
        r['date'] = r['date'].date()
    return result

def get_delivery_note_data():
    dn = DocType('Delivery Note')
    dni = DocType('Delivery Note Item')
    i = DocType('Item')
    
    query = (frappe.qb
        .from_(dn)
        .left_join(dni).on(dni.parent == dn.name)
        .left_join(i).on(dni.item_code == i.name)
        .where(
            (dn.posting_date >= '2023-08-29') &
            (dn.docstatus == 1) &
            (i.item_group == 'Geyser Unit')
        )
        .select(
            dni.qty.as_('net_sales'),
            dn.posting_date.as_('date'),
            dn.customer.as_('customer')
        )
    )
    result = query.run(as_dict=True)
    return result

def get_inactive_customers():
    datediff = CustomFunction("DATEDIFF", ["cur_date", "end_date"])
    so = DocType('Sales Order')
    query = (frappe.qb
        .from_(so)
        .where(so.docstatus == 1)
        .select(so.customer.as_('customer'),
                Count(so.name).as_('no_of_so'),
                Max(so.transaction_date).as_('last_order_date'),
                datediff(CurDate(), Max(so.transaction_date)).as_('days_since_last_order')
        )
        .groupby(so.customer)
    )
    return query.run(as_dict=True)

def get_customer():
    cu = DocType('Customer')
    query = (frappe.qb
        .from_(cu)
        .select(cu.name.as_('customer'), cu.customer_group, cu.customer_name)         
    )
    return query.run(as_dict=True)

def join(filters):
    from frappe.utils import getdate
    customer_data_list = get_customer()
    transactions_list = get_delivery_note_data() + get_tally_data()
    inactive_customers = get_inactive_customers()

    # Parse the date strings and convert them to datetime objects
    start_date_str = filters.get('from_date')
    end_date_str = filters.get('to_date')
    start_date = getdate(start_date_str)
    end_date = getdate(end_date_str)
    desired_customer_group = filters.get('sales_person')
    desired_customer = filters.get('desired_customer')

    # Create a list to store consolidated data for each customer
    consolidated_data_list = []

    # Iterate through customer data
    for customer_data in customer_data_list:
        if desired_customer_group != 'All' and customer_data['customer_group'] != desired_customer_group:
            continue

        total_net_sales = 0.0
        customer = customer_data['customer']
        customer_name = customer_data['customer_name']
        
        days_since_last_order = 0.0
        last_order_date = datetime.date.today()
        no_of_so = 0.0
        for inactive_cust in inactive_customers:
            if(inactive_cust['customer'] == customer):
                days_since_last_order = inactive_cust['days_since_last_order']
                last_order_date = inactive_cust['last_order_date']
                no_of_so = inactive_cust['no_of_so']
        
        for transaction in transactions_list:
            if (
                start_date <= transaction['date'] <= end_date
                and (desired_customer == "All" or transaction['customer'] == customer)
            ):
                total_net_sales += transaction['net_sales']
            
        if total_net_sales != 0.0:
            consolidated_data = {
                'customer': customer,
                'customer_name': customer_name,
                'net_sales': total_net_sales,
                'days_since_last_order': days_since_last_order,
                'last_order_date': last_order_date,
                'no_of_so': no_of_so
            }
            if consolidated_data:
                consolidated_data_list.append(consolidated_data)
    
    if not consolidated_data_list:
        return []
    else:
        consolidated_data_list.sort(key=lambda x: x['net_sales'], reverse=True)
        return consolidated_data_list

def get_columns(filters):
    columns = [
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 250,
        },
        {
            "label": "Net Sales",
            "fieldname": "net_sales",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "label": "No of SO",
            "fieldname": "no_of_so",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "label": "Days Since Last Order",
            "fieldname": "days_since_last_order",
            "fieldtype": "Int",
            "width": 120,
        },
        {
            "label": "Last SO Date",
            "fieldname": "last_order_date",
            "fieldtype": "Date",
            "width": 120,
        }
    ]
    return columns


def get_conditions(filters):
    conditions = "net_sales > 0"
    if filters and filters.get("from_date"):
        from_date = filters.get("from_date")
        conditions += f" AND d.date >= '{from_date}'"
    if filters and filters.get("to_date"):
        to_date = filters.get("to_date")
        conditions += f" AND d.date <= '{to_date}'"
    if filters and filters.get("sales_person"):
        sales_person = filters.get("sales_person")
        if sales_person == 'All':
            conditions += f" AND 1"
        else:
            conditions += f" AND d.salesman = '{sales_person}'"
    return conditions


def get_data(filters):
    return
    query = f"""
        SELECT
            customer,
            salesman,
            SUM(net_sales) AS net_sales
        FROM (
            SELECT
                SUM(IF(td.transaction_type = 'Sales', td.quantity, - (td.quantity))) AS net_sales,
                tp.customer AS customer,
                cu.customer_group AS salesman,
                td.date AS date
            FROM
                `tabTally April to August 2023` AS td
                LEFT JOIN `tabTally Party Name` AS tp ON td.party_name = tp.name
                LEFT JOIN `tabTally Particular` as tr ON td.particulars = tr.name
                LEFT JOIN `tabCustomer` AS cu ON tp.customer = cu.name
                LEFT JOIN `tabItem` as i ON i.name = tr.item
            WHERE
                td.date BETWEEN '2023-04-01' AND '2023-08-28'
                AND i.item_group = 'Geyser Unit'
            GROUP BY
                tp.customer

            UNION
            
            SELECT
                SUM(dni.qty) AS net_sales,
                dn.customer_name AS customer,
                cu.customer_group AS salesman,
                dn.posting_date AS date
            FROM
                `tabDelivery Note` AS dn
                LEFT JOIN `tabDelivery Note Item` as dni ON dni.parent = dn.name
                LEFT JOIN `tabCustomer` AS cu ON dn.customer_name = cu.customer_name
                LEFT JOIN `tabItem` as i ON dni.item_code = i.name
            WHERE
                dn.posting_date >= '2023-08-29'
                AND dn.docstatus = 1
                AND i.item_group = 'Geyser Unit'
            GROUP BY
                dn.customer_name
            HAVING
                MAX(dn.posting_date) >= '2023-08-29'
        ) AS d
        WHERE {get_conditions(filters)}
        GROUP BY
            d.customer
        ORDER BY
            net_sales DESC
    """

    result = frappe.db.sql(query, as_dict=True)
    return result
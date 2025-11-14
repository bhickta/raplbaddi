import frappe

def update_total_amount(dsra_doc):
    dsra = frappe.get_doc('Daily Sales Report By Admin', dsra_doc.name)
    expense = dsra.amount_for_travel
    for e in dsra.daily_sales_expenses_by_admin:
        expense += e.amount
    dsra.total_amount = expense
    if not dsra.date:
        dsra.date = dsra.creation
    dsra.save()

def update():
    for dsra in frappe.get_all('Daily Sales Report By Admin', filters={'docstatus': 1}):
        update_total_amount(dsra)

def hello():
    print('hello')

@frappe.whitelist()
def get_customer_details(customer):
    return frappe.db.sql(f"""
        SELECT customer_address, customer_phone_number, serial_no, brand, model
        FROM `tabSupport Customer`
        WHERE name='{customer}'
    """, as_dict=True)

@frappe.whitelist()
def get_dpi_parent(sno):
       return frappe.db.sql(f"""
        SELECT parent FROM `tabDaily Production Item` as dpi
        WHERE dpi.name='{sno}'
    """, as_dict=True)

@frappe.whitelist()
def get_last_so_of_customer(customer=None):
    filter =  {'customer': customer}
    try:
        so = frappe.get_last_doc('Sales Order', filters=filter)
        return so
    except:
        return "Doc not found"

@frappe.whitelist()
def price_list_of_customer(customer=None):
    try:
        price_list = frappe.db.sql(f"""
            SELECT soi.item_code, soi.rate, soi.discount_amount, MAX(so.transaction_date) AS latest_transaction_date
            FROM `tabSales Order Item` AS soi
            JOIN `tabSales Order` AS so ON so.name = soi.parent
            WHERE so.customer = '{customer}' AND so.docstatus = 1
            GROUP BY so.customer, soi.item_code
        """, as_dict=True
        )
        return price_list
    except:
        return "Doc not Found"

@frappe.whitelist()
def get_task(user=None, frequency=None):
    try:
        task = frappe.db.sql(f"""
            SELECT name
            FROM `tabTask Rapl`
            WHERE '{user}' IN (user_kaccha, user_pakka, user_assistant) AND frequency = '{frequency}';
        """, as_dict=True
        )
        return task
    except:
        return "No Task Found"


def get_fields(doctype, fields=None):
    from frappe.utils import unique
    if fields is None:
        fields = []
    meta = frappe.get_meta(doctype)
    fields.extend(meta.get_search_fields())

    if meta.title_field and not meta.title_field.strip() in fields:
        fields.insert(1, meta.title_field.strip())

    return unique(fields)

from frappe.desk.reportview import get_filters_cond, get_match_cond
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_poi_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    doctype = "Purchase Order"
    print(txt)
    conditions = []   
    q = """SELECT poi.item_code as item_code, poi.qty - poi.received_qty as received_qty
                FROM `tabPurchase Order Item` AS poi
                JOIN `tabPurchase Order` ON `tabPurchase Order`.name = poi.parent
                WHERE 1
                    {fcond} {mcond}
                    AND poi.item_code LIKE %(txt)s
                    AND poi.qty - poi.received_qty > 0
                ORDER BY
                    poi.qty - poi.received_qty DESC
                LIMIT {start}, {page_len}              
                """.format(
                **{
                    "key": searchfield,
                    "fcond": get_filters_cond(doctype, filters, conditions),
                    "mcond": get_match_cond(doctype),
                    "start": start,
                    "page_len": page_len,
                }
            )
    return frappe.db.sql(
        q, {"txt": "%%%s%%" % txt}, as_dict=as_dict)
    
@frappe.whitelist()
def get_poi(item_code):
    po = frappe.qb.DocType('Purchase Order')
    poi = frappe.qb.DocType('Purchase Order Item')
    query = (
        frappe.qb
        .from_(poi)
        .join(po).on(po.name == poi.parent)
        .where(po.docstatus == 1)
        .where(po.status != 'Closed')
        .where(poi.qty - poi.received_qty > 0)
        .where(poi.item_code == item_code)
        .select(
            poi.material_request_item.as_('material_request_item'), poi.material_request,
            (poi.qty - poi.received_qty).as_('remaining_qty'),
            poi.name.as_('purchase_order_item'), poi.parent.as_('purchase_order'),
            poi.rate.as_('rate'),
        )
    )
    return query.run(as_dict=True)

@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_mr_query(doctype, txt, searchfield, start, page_len, filters, as_dict=False):
    doctype = "Material Request"
    print(txt)
    conditions = []   
    q = """SELECT mri.item_code as item_code, mri.qty - mri.ordered_qty as remaining_for_order_qty
                FROM `tabMaterial Request Item` AS mri
                JOIN `tabMaterial Request` ON `tabMaterial Request`.name = mri.parent
                WHERE 1
                    {fcond} {mcond}
                    AND mri.item_code LIKE %(txt)s
                    AND mri.qty - mri.ordered_qty > 0
                ORDER BY
                    mri.qty - mri.ordered_qty DESC
                LIMIT {start}, {page_len}              
                """.format(
                **{
                    "key": searchfield,
                    "fcond": get_filters_cond(doctype, filters, conditions),
                    "mcond": get_match_cond(doctype),
                    "start": start,
                    "page_len": page_len,
                }
            )
    return frappe.db.sql(
        q, {"txt": "%%%s%%" % txt}, as_dict=as_dict)

@frappe.whitelist()
def get_mr(item_code):
    mr = frappe.qb.DocType('Material Request')
    mri = frappe.qb.DocType('Material Request Item')
    query = (
        frappe.qb
        .from_(mri)
        .join(mr).on(mr.name == mri.parent)
        .where(mr.docstatus == 1)
        .where(mr.status != 'Stopped')
        .where(mri.qty - mri.ordered_qty > 0)
        .where(mri.item_code == item_code)
        .select(
            mri.name.as_('material_request_item'), mri.parent.as_('material_request'),
            (mri.qty - mri.ordered_qty).as_('remaining_for_order_qty')
        )
    )
    return query.run(as_dict=True)

def get_bin_details(bin_name):
	return frappe.db.get_value(
		"Bin",
		bin_name,
		[
			"actual_qty",
			"ordered_qty",
			"reserved_qty",
			"indented_qty",
			"planned_qty",
			"reserved_qty_for_production",
			"reserved_qty_for_sub_contract",
			"reserved_qty_for_production_plan",
            "sales_order_reserved_qty"
		],
		as_dict=1,
	)

from erpnext.stock import utils
import ast
@frappe.whitelist()
def reserve_qty_of_so(items, reserve_type):
    so_items = ast.literal_eval(items)
    for item in so_items:
        item_code = item.get('item_code')
        warehouse = item.get('warehouse')
        sales_order_reserved_qty = item.get('qty')
        bin = utils.get_bin(item_code, warehouse)
        if reserve_type == "reserve":
            bin.sales_order_reserved_qty = max(0, bin.sales_order_reserved_qty + sales_order_reserved_qty)
        if reserve_type == "unreserve":
            bin.sales_order_reserved_qty = max(0, bin.sales_order_reserved_qty - sales_order_reserved_qty)
        bin.save()
        print(bin.sales_order_reserved_qty)
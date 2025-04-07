import frappe
from raplbaddi.utils import report_utils
from pypika import Case

def get_so_items(filters=None):
	so = frappe.qb.DocType('Sales Order')
	soi = frappe.qb.DocType('Sales Order Item')
	query = (
		frappe.qb
		.from_(so)
		.left_join(soi).on(so.name == soi.parent)
		.where(so.status.notin(['Stopped', 'Closed']) & so.docstatus == 1)
		.where(so.delivery_status.isin(['Partly Delivered', 'Not Delivered']))
		.select(
			Case().when(so.submission_date, so.submission_date).else_(so.transaction_date).as_('date'),
			soi.item_code.as_('item_code'),
			so.status.as_('status'),
			so.customer.as_('customer'),
			so.customer_name.as_('customer_name'),
			so.conditions.as_('so_remarks'),
			soi.custom_box.as_('box'),
			so.planning_remarks.as_('planning_remarks'),
			so.dispatch_remarks.as_('dispatch_remarks'),
			so.shipping_address_name.as_('shipping_address_name'),
			so.name.as_('sales_order'),
			soi.item_code.as_('item_code'),
			soi.qty.as_('qty').as_('ordered_qty'),
			soi.delivered_qty.as_('delivered_qty'),
			report_utils.Greatest(0, soi.qty - soi.delivered_qty).as_('pending_qty'),
			(soi.stock_reserved_qty).as_('stock_reserved_qty'),
			soi.warehouse.as_('brand'),
			soi.color.as_('color'),
			so.delivery_status,
			so.delivery_status.as_('delivery_status')
		)
	)
	if filters and filters.get('item_group'):
		query = query.where(soi.item_group.isin(filters.get('item_group')))
	data = query.run(as_dict=True)
	return data

def get_bin_stock():
	bin = frappe.qb.DocType('Bin')
	query = (
		frappe.qb
		.from_(bin)
		.select(bin.item_code, bin.warehouse, bin.actual_qty)
	)
	return query.run(as_dict=True)

def get_box_qty():
    from raplbaddi.stock_rapl.report.pb_report.box_data import BoxRequirements
    box = BoxRequirements()
    box_qty = box.warehouse_qty()
    return box_qty

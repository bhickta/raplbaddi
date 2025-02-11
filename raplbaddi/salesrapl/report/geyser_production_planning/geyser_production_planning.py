# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt
from frappe import _
from raplbaddi.utils import report_utils
from raplbaddi.salesrapl.report.geyser_production_planning import sales_order_data
import frappe
from collections import Counter

def execute(filters=None):
	columns, data = [], []
	if filters.get('report_type') == "Order and Shortage":
		data = order_and_shortage_data(filters)
	elif filters.get('report_type') == "Itemwise Order and Shortage":
		data = itemwise_order_and_shortage_data(filters)
	return get_columns(filters), data

def itemwise_order_and_shortage_data(filters):
	data = sales_order_data.get_so_items(filters)
	bin = sales_order_data.get_bin_stock()
	boxes = sales_order_data.get_box_qty()
	item_units = {}
    
	for soi in data:
		brand = soi['brand'] = soi['brand'].replace('- RAPL', '')
		item_name = soi['item_name'] = soi['item_code'] + ' ' + brand

		for bin_val in bin:
			if bin_val['item_code'] == soi['item_code'] and bin_val['warehouse'].replace('- RAPL', '') == soi['brand']:
				short = 0
				if bin_val['actual_qty'] - soi['pending_qty'] > 0:
					short = 0
				else:
					short = soi['pending_qty'] - bin_val['actual_qty']
				soi['%'] = 100 - (short / soi['pending_qty']) * 100
				soi['actual_qty'] = bin_val['actual_qty']
				soi['short_qty'] = short
				city = get_city_from_shipping(soi.get('shipping_address_name', None))
				soi["city"] = city
    
		for box in boxes:
			if box.get('box') == soi['box']:
				soi['box_stock_qty'] = box['warehouse_qty']

		if soi['item_code'] not in item_units:
			item_units[soi['item_code']] = frappe.get_cached_value("Item", soi['item_code'], "unit")

	for d in data:
		d['unit'] = item_units[d['item_code']]

	set_box_ordered_data(data)
	for d in data:
		d['box_short_qty'] = d['short_qty'] - d.get('box_order', 0) - d.get('box_stock_qty', 0)

	append_city_count(data)
	data.sort(reverse=True, key= lambda entry: entry['%'])
	return data

def set_box_ordered_data(data):
	box_order_data = get_ordered_qty()
	box_ordered = {}
	for d in box_order_data:
		box_ordered[d.item_code] = {"ordered": d.ordered, "supplier": d.supplier}
	for d in data:
		box_detail = box_ordered.get(d.get('box'), {})
		d['box_order'] = box_detail.get("ordered", 0)
		d['supplier'] = box_detail.get("supplier", None)

def append_city_count(data):
	city_counts = Counter(d['city'] for d in data)
	for d in data:
		d['city_count'] = city_counts[d['city']]

def get_ordered_qty():
    query = f"""
		SELECT
			poi.item_code, 
			SUM(GREATEST(qty - received_qty, 0)) AS ordered,
			po.supplier
		FROM
			`tabPurchase Order Item` poi
			JOIN `tabPurchase Order` po ON po.name = poi.parent
		WHERE
			po.docstatus = 1
			AND po.status NOT IN ('Stopped', 'Closed')
			AND poi.item_group = 'Packing Boxes'
		GROUP BY
			poi.item_code
    """
    return frappe.db.sql(query, as_dict=True)

def order_and_shortage_data(filters):
	data = []
	so = report_utils.accum_mapper(data=(sales_order_data.get_so_items(filters)), key='sales_order')
	bin = sales_order_data.get_bin_stock()
	for so, so_val in so.items():
		entry = {}
		entry['sales_order'] = so
		entry['pending_qty'] = 0
		entry['so_shortage'] = 0
		entry['so_shortage'] = 0
		items, brands = set(), set()
		for soi in so_val:
			city = get_city_from_shipping(soi.get('shipping_address_name', None))
			entry["city"] = city
			entry['pending_qty'] += soi['pending_qty']
			entry['status'] = soi['status']
			entry['planning_remarks'] = soi['planning_remarks']
			entry['dispatch_remarks'] = soi['dispatch_remarks']
			entry['so_remarks'] = soi['so_remarks']
			entry['date'] = soi['date']
			entry['customer'] = soi['customer']
			entry['customer_name'] = soi['customer_name']
			soi_shortage = 0
			items.add(soi['item_code'])
			brands.add(soi['brand'].replace(' - RAPL', ''))
			for bin_val in bin:
				if bin_val['item_code'] == soi['item_code'] and bin_val['warehouse'] == soi['brand']:
					short = 0
					if bin_val['actual_qty'] - soi['pending_qty'] > 0:
						short = 0
					else:
						short = soi['pending_qty'] - bin_val['actual_qty']
					soi_shortage += short
			entry['so_shortage'] += soi_shortage
		entry['items'] = ', '.join(items)
		entry['brands'] = ', '.join(brands)
		entry['%'] = 100 - (entry['so_shortage'] / entry['pending_qty']) * 100
		entry["color"] = soi["color"]
		data.append(entry)
	append_city_count(data)
	data.sort(reverse=True, key= lambda entry: entry['%'])
	return data

def get_columns(filters=None):
	cols = None
	if filters.get('report_type') == 'Itemwise Order and Shortage':
		builder = report_utils.ColumnBuilder()
		cols = (builder
			.add_column("Order Date", "Date", 100, "date")
			.add_column("Planning Remarks", "HTML", 100, "planning_remarks")
			.add_column("Dispatch Remarks", "HTML", 100, "dispatch_remarks")
			.add_column("SO Number", "Link", 100, "sales_order", options="Sales Order")
			.add_column("City", "Data", 100, "city", options="")
			.add_column("City Count", "Int", 100, "city_count", options="")
			.add_column("Customer", "Link", 300, "customer", options="Customer")
			.add_column("Item", "Data", 100, "item_code", options="")
			.add_column("Brand", "Data", 100, "brand")
			.add_column("Color", "Data", 100, "color")
			.add_column("Order Qty", "Int", 120, "pending_qty")
			.add_column("Actual Qty", "Int", 120, "actual_qty")
			.add_column("Short Qty", "Int", 120, "short_qty")
			.add_column("Item Name", "Data", 130, "item_name")
   			.add_column("SO Remark", "HTML", 130, "so_remarks")
			.add_column("Box name", "Link", 100, "box", options="Item")
			.add_column("Box Qty", "Int", 120, "box_stock_qty")
			.add_column("Box Shortage", "Int", 120, "box_short_qty")
			.add_column("Box Order", "HTML", 130, "box_order")
			.add_column("Supplier", "Data", 120, "supplier")
			.add_column("Unit", "Data", 130, "unit")
			.build()
		)
	if filters.get('report_type') == 'Order and Shortage':
		builder = report_utils.ColumnBuilder()
		cols = (builder
			.add_column("Date", "Date", 100, "date")
			.add_column("Items", "Data", 100, "items")
			.add_column("Planning Remarks", "HTML", 100, "planning_remarks")
			.add_column("Dispatch Remarks", "HTML", 100, "dispatch_remarks")
			.add_column("Status", "Data", 100, "status")
			.add_column("Sales Order", "Link", 100, "sales_order", options="Sales Order")
			.add_column("City", "Data", 100, "city", options="")
			.add_column("City Count", "Int", 100, "city_count", options="")
			.add_column("Customer", "Link", 300, "customer", options="Customer")
			.add_column("Order Qty", "Int", 120, "pending_qty")
			.add_column("Shortage Qty", "Int", 100, "so_shortage")
			.add_column("% Available", "Int", 100, "%", disable_total=True)
			.add_column("Brand", "Data", 100, "brands")
			.add_column("SO Remark", "HTML", 130, "so_remarks")
			.build()
		)
	return cols

def get_city_from_shipping(shipping_address):
    return frappe.get_value("Address", shipping_address, "city")
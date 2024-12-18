# Copyright (c) 2024, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import Order


def execute(filters=None):
	report_type = ReportType(filters)
	report = report_type.get_report_class()(filters)
	data = report.get_data()
	columns = report.get_columns()
	return columns, data

class ReportType:
	def __init__(self, filters):
		self.filters = filters
		self.set_report_type_class_map()

	def set_report_type_class_map(self):
		self.report_type_class_map = {
			"Packing Box Stock Report": PBReportNew,
		}
	
	def get_report_class(self):
		return self.report_type_class_map.get(self.filters.report_type)


class PBReportNew:
	def __init__(self, filters):
		self.filters = filters
		self.pb_warehouses = frappe.get_list("Warehouse", {"warehouse_type": "Packing Box"}, pluck="name")

	def get_data(self):
		data = []
		pb_stock_details = self.get_stock_details(self.pb_warehouses, "Packing Boxes", self.filters.is_group_by)
		if not pb_stock_details:
			return data
		data = self.create_data(pb_stock_details)
		return data

	def create_data(self, pb_stock_details):
		data = pb_stock_details
		return data

	def pb_items(self):
		return frappe.get_all("Item", fields=["name", "item_name"], filters={"item_group": "Packing Boxes"})

	def get_stock_details(self, warehouse: tuple, item_group=None, group_by=False, item_code=None):
		item_table = frappe.qb.DocType("Item")
		bin_table = frappe.qb.DocType("Bin")

		query = (
			frappe.qb.from_(item_table)
			.join(bin_table)
			.on(bin_table.item_code == item_table.name)
			.select(
				bin_table.item_code,
				bin_table.actual_qty,
				item_table.item_name,
			)
			.where(bin_table.warehouse.isin(warehouse))
			.orderby(bin_table.item_code, order=Order.asc)
			.orderby(item_table.item_name, order=Order.asc)
			.orderby(bin_table.warehouse, order=Order.asc)
			.orderby(bin_table.actual_qty, order=Order.asc)
		)
  
		item_code = item_code or self.filters.item_code
		if item_code:
			query = query.where(bin_table.item_code == item_code)

		if item_group:
			query = query.where(item_table.item_group == item_group)

		if self.filters.warehouse:
			query = query.where(bin_table.warehouse == self.filters.warehouse)

		if group_by:
			query = query.groupby(bin_table.item_code)
		else:
			query = query.select(bin_table.warehouse)

		return query.run(as_dict=True)

	def get_columns(self):
		columns = []
		self.set_columns(columns)
		self.set_column_defaults(columns)
		return columns

	def set_columns(self, columns):
		columns.append(frappe._dict({"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item",}))
		columns.append(frappe._dict({"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data",}))
		columns.append(frappe._dict({"label": "Stock Qty", "fieldname": "actual_qty", "fieldtype": "Float",}))
		if not self.filters.is_group_by:
			columns.append(frappe._dict({"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse",}))
  
	def set_column_defaults(self, columns):
		for col in columns:
			if not col.width:
				col.width = 150
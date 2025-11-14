# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Sum
from pypika.terms import Case, Not, Field, Order
from frappe.query_builder import AliasedQuery
from frappe.utils import getdate
from raplbaddi.datarapl.doctype.report_full_access_users.report_full_access_users import get_wildcard_users
from frappe.query_builder.functions import Concat, Sum, GroupConcat
from frappe.utils import get_url
from raplbaddi.stock_rapl.report.pb_report.box_data import BoxRequirements
from raplbaddi.utils import report_utils

box_data = BoxRequirements()
date = getdate('1-1-1')

def execute(filters=None):
    return columns(filters), join(filters)

def join(filters=None):
    all_box = box_data.all_boxes()
    supplier, warehouse = box_data.get_supplier_and_warehouse(filters=filters)
    warehouse_box = report_utils.get_mapped_data(data=box_data.warehouse_qty(warehouse), str='box')
    po_box = report_utils.get_mapped_data(data=box_data.get_supplierwise_po(supplier), str='box')


    filtered_box = []

    for box in all_box:
        box_name = box['box']

        if box_name in warehouse_box:
            box['warehouse_qty'] = warehouse_box[box_name]['warehouse_qty']
        else:
            box['warehouse_qty'] = 0.0

        if box_name in po_box:
            box['box_qty'] = po_box[box_name]['box_qty']
            box['planned_qty'] = po_box[box_name]['planned_qty']
            box['over_dispatch'] = po_box[box_name]['over_dispatch']
            box['po_name'] = po_box[box_name]['po_name']
            box['po_date'] = po_box[box_name]['po_date']
        else:
            box['box_qty'] = 0.0
            box['planned_qty'] = 0.0
            box['po_date'] = date

        if box['warehouse_qty'] != 0.0 or box['box_qty'] != 0.0 or box['planned_qty'] != 0.0:
            filtered_box.append(box)

    filtered_box.sort(key=lambda x: x['po_date'], reverse=True)
    return filtered_box

def columns(filters=None):
    builder = report_utils.ColumnBuilder()
    cols = (
        builder
        .add_column('Item', 'Link', 180, 'box', options='Item')
        .add_column('Date', 'Date', 120, 'po_date')
        .add_column('Stock', 'Int', 60, 'warehouse_qty')
        .add_column('Production Order', 'Int', 100, 'box_qty')
        .add_column('Dispatch Order', 'Int', 100, 'planned_qty')
        .add_column('Over Dispatch', 'Int', 100, 'over_dispatch')
        .add_column('PO', 'Html', 100, 'po_name')
        .build()
    )
    return cols
# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Sum
from pypika.terms import Case, Not, Field, Order
from frappe.query_builder import AliasedQuery
from raplbaddi.datarapl.doctype.report_full_access_users.report_full_access_users import get_wildcard_users

def permissions():
    pass

def execute(filters=None):
    return columns(filters), data(filters)
   
def data(filters=None):
    
    item = DocType('Item')
    bin = DocType('Bin')
    soi = DocType('Sales Order Item')
    so = DocType('Sales Order')
    poi = DocType('Purchase Order Item')
    po = DocType('Purchase Order')
      
    rapl_qty = negate_null_negative(bin.actual_qty)
    safe_qty = negate_null_negative(item.safety_stock)
    
    aso, sales_order = AliasedQuery('aso'), frappe.qb.from_(soi).left_join(so).on(so.name == soi.parent).where(so.docstatus == 1).where(Not(so.status.isin(['Stopped', 'Closed']))).select(Sum(soi.qty - soi.delivered_qty).as_('box_qty'), soi.custom_box.as_('box')).groupby(soi.custom_box)
    so_qty = negate_null_negative(aso.box_qty)
    
    aapo = AliasedQuery('apo')
    a_purchase_order = frappe.qb.from_(poi).left_join(po).on(po.name == poi.parent).where(po.supplier == "Amit Print 'N' Pack, Kishanpura, Baddi").where(po.docstatus == 1).select(Sum(poi.qty - poi.received_qty).as_('box_qty'), poi.item_code.as_('box'), Sum(poi.planned_dispatch_qty - poi.received_qty).as_('planned_qty')).groupby(poi.item_code)
    pa_qty = negate_null_negative(aapo.box_qty)
    da_qty = negate_null_negative(aapo.planned_qty)
    
    ajpo = AliasedQuery('jpo')
    j_purchase_order = frappe.qb.from_(poi).left_join(po).on(po.name == poi.parent).where(po.supplier == "Jai Ambey Industries").where(po.docstatus == 1).select(Sum(poi.qty - poi.received_qty).as_('box_qty'), poi.item_code.as_('box'), Sum(poi.planned_dispatch_qty - poi.received_qty).as_('planned_qty')).groupby(poi.item_code)
    pj_qty = negate_null_negative(ajpo.box_qty)
    dj_qty = negate_null_negative(ajpo.planned_qty)
      
    ja, jai_ambey = AliasedQuery('ja'), frappe.qb.from_(bin).where(bin.warehouse == 'Jai Ambey Industries - RAPL').select(bin.item_code, bin.actual_qty)
    j_qty =  negate_null_negative(ja.actual_qty)
    
    
    am, amit = AliasedQuery('am'), frappe.qb.from_(bin).where(bin.warehouse == "Amit Print 'N' Pack - RAPL").select(bin.item_code, bin.actual_qty)
    a_qty =  negate_null_negative(am.actual_qty)
    short_qty = negate_null_negative(so_qty + safe_qty - pa_qty - pj_qty - rapl_qty - j_qty - a_qty)
    
    query = (
        frappe.qb
        .from_(item).where(item.item_group == 'Packing Boxes')
        .left_join(bin).on(item.name == bin.item_code).where(bin.warehouse == 'Packing Boxes - Rapl')
        .with_(sales_order, 'aso').with_(a_purchase_order, 'apo').with_(j_purchase_order, 'jpo').with_(jai_ambey, 'ja').with_(amit, 'am')
        .left_join(aso).on(aso.box == item.item_code)
        .left_join(aapo).on(aapo.box == item.item_code)
        .left_join(ajpo).on(ajpo.box == item.item_code)
        .left_join(ja).on(ja.item_code == item.item_code)
        .left_join(am).on(am.item_code == item.item_code)
        .select(item.name, safe_qty, so_qty, rapl_qty, a_qty, j_qty, pa_qty, da_qty, pj_qty, dj_qty, short_qty)
        .orderby(short_qty, order=Order.desc)
    )
    return query.run()

def negate_null_negative(data: Field) -> Case:
    return (Case().when((data).isnull(), 0)
         .else_(
             Case().when((data) < 0, 0)
                  .else_((data))
         ))

def columns(filters=None):
   cols = [{"label": "item", "fieldtype": "Link", "width": 180, "options": "Item"},
        {"label": "MSL", "fieldtype": "Int", "width": 60, "disable_total": True},
        {"label": "SO", "fieldtype": "Int", "width": 60},
        {"label": "RAPL", "fieldtype": "Int", "width": 60},
        {"label": "Amit", "fieldtype": "Int", "width": 60},
        {"label": "JAI", "fieldtype": "Int", "width": 60},
        {"label": "Prod Amit", "fieldtype": "Int", "width": 100},
        {"label": "Disp Amit", "fieldtype": "Int", "width": 100},
        {"label": "Prod JAI", "fieldtype": "Int", "width": 100},
        {"label": "Disp JAI", "fieldtype": "Int", "width": 100},
        {"label": "Shortage", "fieldtype": "Int", "width": 100}
    ]
   return cols
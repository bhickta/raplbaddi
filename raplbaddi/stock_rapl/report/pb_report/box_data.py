from frappe.query_builder import DocType
from frappe.query_builder.functions import Concat, Sum, GroupConcat, Coalesce
from pypika import Case
from frappe.utils import get_url
from raplbaddi.utils import report_utils
import frappe

class BoxRequirements:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BoxRequirements, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        self.url = get_url()
        self.items = DocType('Item')
        self.bin = DocType('Bin')
        self.so = DocType('Sales Order')
        self.soi = DocType('Sales Order Item')
        self.mr = DocType("Material Request")
        self.mr_item = DocType("Material Request Item")
        self.poi = DocType('Purchase Order Item')
        self.po = DocType('Purchase Order')
        self.psp = DocType('Paper Supplier Priority')

    def get_paper_supplier_priority(self, supplier):
        query = (
            frappe.qb
            .from_(self.psp)
            .left_join(self.items)
            .on(self.items.paper_name == self.psp.paper_name)
            .where(self.psp.supplier == supplier)
            .where(Coalesce(self.items.brand, self.items.plain_box_type) == self.psp.parent)
            .select(self.psp.paper_name, self.psp.supplier, self.psp.priority, self.psp.parent.as_('box_particular'), self.items.name.as_('box'))
        )
        return query.run(as_dict=True)
    
    def all_boxes(self, item_group, key):
        box_query = (
            frappe.qb
            .from_(self.items)
            .where(self.items.item_group == item_group)
            .where(self.items.disabled == 0)
            .select(self.items.name.as_(key), self.items.safety_stock.as_('msl'), self.items.dead_inventory.as_('dead_inventory'), self.items.rapl_msl.as_('rapl_msl'), self.items.paper_name.as_('paper_name'), Coalesce(self.items.brand, self.items.plain_box_type, '').as_('box_particular')
            )
        )
        return box_query.run(as_dict=True)
    
    def warehouse_qty(self, warehouse=None):
        qty_query = (
            frappe.qb
            .from_(self.items)
            .left_join(self.bin)
            .on(self.items.name == self.bin.item_code)
            .select(
                Sum(self.bin.actual_qty).as_('warehouse_qty'),
                self.items.name.as_('box'),
                self.bin.projected_qty.as_('projected_qty')
            )
            .groupby(self.items.name)
        )
        if warehouse:
            qty_query = qty_query.where(self.bin.warehouse == warehouse)
        else:
            pb_warehouses = frappe.get_list("Warehouse", {"warehouse_type": "Packing Boxes"}, pluck="name")
            qty_query = qty_query.where(self.bin.warehouse.isin(pb_warehouses))
        return report_utils.remove_negative(['warehouse_qty'], qty_query.run(as_dict=True))

    def get_box_requirement_from_so(self):
        so_query = (
            frappe.qb
            .from_(self.so)
            .left_join(self.soi)
            .on(self.so.name == self.soi.parent)
            .where(self.so.docstatus == 1)
            .where(self.so.status.notin(['Stopped', 'Closed']))
            .where((self.soi.qty - self.soi.delivered_qty) > 0)
            .select(
                Sum(self.soi.qty - self.soi.delivered_qty).as_('so_qty'),
                self.soi.custom_box.as_('box'),
                GroupConcat(Concat('<a href="', self.url, '/app/sales-order/', self.so.name, '">', self.so.name, '</a>')).as_('so_name')
            )
            .groupby(self.soi.custom_box)
        )
        return so_query.run(as_dict=True)

    def get_box_order_for_production(self, supplier):
        query = (
            frappe.qb.from_(self.mr)
            .join(self.mr_item)
            .on(self.mr_item.parent == self.mr.name)
            .select(
                self.mr_item.item_code.as_("box"),
                (Sum(Coalesce(self.mr_item.qty, 0))).as_("qty"),
                GroupConcat(Concat('<a href="', self.url, '/app/material-request/', self.mr.name, '">', self.mr.name, '</a>')).as_('mr_name')
            )
            .where(
                (self.mr.material_request_type == "Purchase")
                & (self.mr.docstatus == 1)
                & (self.mr.status != "Stopped")
                & (self.mr.custom_status != "Stopped")
                & (self.mr.per_received < 100)
                & (self.mr.supplier == supplier)
            )
        )

        query = query.groupby(self.mr_item.item_code).orderby(self.mr.transaction_date, self.mr.schedule_date)
        data = query.run(as_dict=True)
        return data

    def get_supplierwise_po(self, supplier):
        query = (
            frappe.qb
            .from_(self.poi)
            .left_join(self.po)
            .on(self.po.name == self.poi.parent)
            .where(self.po.supplier == supplier)
            .where(self.po.docstatus == 1)
            .where(self.po.status != 'Closed')
            .where(self.poi.closed == 0)
            .select(
                Sum(Case()
                    .when(
                        (self.poi.qty - self.poi.received_qty) < 0, (self.poi.qty - self.poi.received_qty) - (self.poi.qty - self.poi.received_qty))
                    .else_((self.poi.qty - self.poi.received_qty))
                ).as_('box_qty'),
                self.poi.item_code.as_('box'),
                Sum(Case()
                    .when(
                        (self.poi.planned_dispatch_qty - self.poi.received_qty) < 0, (self.poi.planned_dispatch_qty - self.poi.received_qty) - (self.poi.planned_dispatch_qty - self.poi.received_qty))
                    .else_((self.poi.planned_dispatch_qty - self.poi.received_qty))
                ).as_('planned_qty'),
                (Case()
                    .when(
                        Sum(self.poi.planned_dispatch_qty - self.poi.received_qty) < 0, Sum(self.poi.received_qty - self.poi.planned_dispatch_qty))
                    .else_(0)
                ).as_('over_dispatch'),
                self.po.transaction_date.as_('po_date'),
                GroupConcat(Concat('<a href="', self.url, '/app/purchase-order/', self.po.name, '">', self.po.name, '</a>')).as_('po_name'),
                Sum(self.poi.received_qty).as_('received_qty')
            )
            .groupby(self.poi.item_code)
        )
        return query.run(as_dict=True)

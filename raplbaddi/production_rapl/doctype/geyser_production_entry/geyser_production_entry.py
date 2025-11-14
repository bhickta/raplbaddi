# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from raplbaddi.utils.stock import make_manufacturing_stock_entry as _make_manufacturing_stock_entry
from raplbaddi.overrides.delivery_note import cancel_reverse_entry_for_internal_customers as _cancel_internal_receipt

class GeyserProductionEntry(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF
        from raplbaddi.production_rapl.doctype.geyser_production_entry_table.geyser_production_entry_table import GeyserProductionEntryTable

        amended_from: DF.Link | None
        contactor_name: DF.Data | None
        date_of_production: DF.Date
        item_group: DF.Link | None
        items: DF.Table[GeyserProductionEntryTable]
        production_line: DF.Link | None
        stock_entry: DF.Data | None
        total: DF.Int
        workforce: DF.Int
    # end: auto-generated types
    pass

    def before_submit(self):
        self.make_manufacturing_stock_entry()
    
    def before_cancel(self):
        self.internal_receipt_name = self.stock_entry
        self.internal_receipt = None

    def on_cancel(self):
        print(self.internal_receipt_name)
        _cancel_internal_receipt(self)

    def make_manufacturing_stock_entry(self):
        items = []
        for item in self.items:
            i = frappe._dict({})
            i.item_code = item.item
            i.qty = item.qty
            i.t_warehouse = item.brand + " - RAPL" if i.item_group not in ["Cooler", "DLP-Price List"] else "FG - RAPL"
            items.append(i)
        self.stock_entry = _make_manufacturing_stock_entry(items=items)
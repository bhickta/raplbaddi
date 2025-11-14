# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesOrderStockReservationEntry(Document):
    def before_save(self):
        if self.sales_order:
            items = frappe.db.get_value("Sales Order", self.sales_order, ["items"])
            self.items = items


@frappe.whitelist()
def make_sales_order_stock_reservation(source_name, target_doc=None, skip_item_mapping=False):
    def set_missing_values(source, target):
        target.update({"sales_order": source.sales_order})

    def update_item(source, target, source_parent):
        target.base_amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(
            source.base_rate
        )
        target.amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.rate)
        target.qty = flt(source.qty) - flt(source.delivered_qty)

        item = get_item_defaults(target.item_code, source_parent.company)
        item_group = get_item_group_defaults(target.item_code, source_parent.company)

        if item:
            target.cost_center = (
                frappe.db.get_value("Project", source_parent.project, "cost_center")
                or item.get("buying_cost_center")
                or item_group.get("buying_cost_center")
            )

    mapper = {
        "Sales Order": {
            "doctype": "Delivery Note",
            "validation": {"docstatus": ["=", 1]},
        },
        "Sales Taxes and Charges": {
            "doctype": "Sales Taxes and Charges",
            "add_if_empty": True,
        },
        "Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
    }

    if not skip_item_mapping:

        def condition(doc):
            # make_mapped_doc sets js `args` into `frappe.flags.args`
            if frappe.flags.args and frappe.flags.args.delivery_dates:
                if cstr(doc.delivery_date) not in frappe.flags.args.delivery_dates:
                    return False
            return (
                abs(doc.delivered_qty) < abs(doc.qty) and doc.delivered_by_supplier != 1
            )

        mapper["Sales Order Item"] = {
            "doctype": "Delivery Note Item",
            "field_map": {
                "rate": "rate",
                "name": "so_detail",
                "parent": "against_sales_order",
            },
            "postprocess": update_item,
            "condition": condition,
        }

    target_doc = get_mapped_doc(
        "Sales Order", source_name, mapper, target_doc, set_missing_values
    )
    target_doc.set_onload("ignore_price_list", True)

    return target_doc

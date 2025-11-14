from erpnext.selling.doctype.sales_order.sales_order import get_item_defaults, get_item_group_defaults

from frappe.model.utils import get_fetch_values
from frappe.contacts.doctype.address.address import get_company_address
from frappe.utils import flt, cstr
from frappe.model.mapper import get_mapped_doc
import frappe

from erpnext.controllers.stock_controller import StockController

@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None, skip_item_mapping=False):
    from erpnext.stock.doctype.packed_item.packed_item import make_packing_list

    def set_missing_values(source, target):
        target.run_method("set_missing_values")
        target.run_method("set_po_nos")
        target.run_method("calculate_taxes_and_totals")

        if source.company_address:
            target.update({"company_address": source.company_address})
        else:
            # set company address
            target.update(get_company_address(target.company))

        if target.company_address:
            target.update(get_fetch_values("Delivery Note", "company_address", target.company_address))

        make_packing_list(target)

    def update_item(source, target, source_parent):
        target.base_amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.base_rate)
        target.amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.rate)
        target.qty = flt(source.qty) - flt(source.delivered_qty)
        target.brand = source.name_of_brand #rapl

        item = get_item_defaults(target.item_code, source_parent.company)
        item_group = get_item_group_defaults(target.item_code, source_parent.company)

        if item:
            target.cost_center = (
                frappe.db.get_value("Project", source_parent.project, "cost_center")
                or item.get("buying_cost_center")
                or item_group.get("buying_cost_center")
            )

    mapper = {
        "Sales Order": {"doctype": "Delivery Note", "validation": {"docstatus": ["=", 1]}},
        "Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "add_if_empty": True},
        "Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
    }

    if not skip_item_mapping:

        def condition(doc):
            # make_mapped_doc sets js `args` into `frappe.flags.args`
            if frappe.flags.args and frappe.flags.args.delivery_dates:
                if cstr(doc.delivery_date) not in frappe.flags.args.delivery_dates:
                    return False
            return abs(doc.delivered_qty) < abs(doc.qty) and doc.delivered_by_supplier != 1

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

    target_doc = get_mapped_doc("Sales Order", source_name, mapper, target_doc, set_missing_values)

    target_doc.set_onload("ignore_price_list", True)
    return target_doc
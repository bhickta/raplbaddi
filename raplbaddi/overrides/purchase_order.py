from .delivery_note import set_naming_series
from .purchase_receipt import posting_datetime_same_as_creation

def before_insert(doc, method):
    set_naming_series(doc)

def set_naming_series(doc):
    naming_series_map = {
        "Real Appliances Private Limited": {
            False: "PO-.YY.-RAPL-.####",
        },
        "Red Star Unit 2": {
            False: "PO-.YY.-RSI-.####",
        }
    }

    if doc.branch in naming_series_map:
        doc.naming_series = naming_series_map[doc.branch][False]
        
def validate(doc, method):
    posting_datetime_same_as_creation(doc)

from erpnext.buying.doctype.purchase_order.purchase_order import PurchaseOrder
from frappe.model.document import frappe, msgprint

class PurchaseOrder(PurchaseOrder):
    
    def remove_fields_from_missing(self, missing):
        if self._action != "save":
            return
        for field, message in missing:
            if field in ["supplier"]:
                missing.remove((field, message))

    def _validate_mandatory(self):
        if self.flags.ignore_mandatory:
            return

        missing = self._get_missing_mandatory_fields()
        for d in self.get_all_children():
            missing.extend(d._get_missing_mandatory_fields())
        
        self.remove_fields_from_missing(missing)
        
        if not missing:
            return

        for idx, msg in missing:  # noqa: B007
            msgprint(msg)

        if frappe.flags.print_messages:
            print(self.as_json().encode("utf-8"))

        raise frappe.MandatoryError(
            "[{doctype}, {name}]: {fields}".format(
                fields=", ".join(each[0] for each in missing), doctype=self.doctype, name=self.name
            )
        )

from erpnext.buying.doctype.purchase_order.purchase_order import flt, get_mapped_doc, set_missing_values, get_party_account, get_item_defaults, get_item_group_defaults

@frappe.whitelist()
def make_purchase_receipt(source_name, target_doc=None):
    def update_item(obj, target, source_parent):
        target.qty = flt(obj.qty) - flt(obj.received_qty)
        target.stock_qty = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.conversion_factor)
        target.amount = (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate)
        target.base_amount = (
            (flt(obj.qty) - flt(obj.received_qty)) * flt(obj.rate) * flt(source_parent.conversion_rate)
        )

    doc = get_mapped_doc(
        "Purchase Order",
        source_name,
        {
            "Purchase Order": {
                "doctype": "Purchase Receipt",
                "field_map": {"supplier_warehouse": "supplier_warehouse", "custom_grand_total": "custom_grand_total", "custom_tax_rate": "custom_tax_rate"},
                "validation": {
                    "docstatus": ["=", 1],
                },
            },
            "Purchase Order Item": {
                "doctype": "Purchase Receipt Item",
                "field_map": {
                    "name": "purchase_order_item",
                    "parent": "purchase_order",
                    "bom": "bom",
                    "material_request": "material_request",
                    "material_request_item": "material_request_item",
                    "sales_order": "sales_order",
                    "sales_order_item": "sales_order_item",
                    "wip_composite_asset": "wip_composite_asset",
                },
                "postprocess": update_item,
                "condition": lambda doc: abs(doc.received_qty) < abs(doc.qty)
                and doc.delivered_by_supplier != 1,
            },
            "Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "reset_value": True},
        },
        target_doc,
        set_missing_values,
    )

    return doc

@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None):
	return get_mapped_purchase_invoice(source_name, target_doc)

def get_mapped_purchase_invoice(source_name, target_doc=None, ignore_permissions=False):
    def postprocess(source, target):
        target.flags.ignore_permissions = ignore_permissions
        set_missing_values(source, target)

        # set tax_withholding_category from Purchase Order
        if source.apply_tds and source.tax_withholding_category and target.apply_tds:
            target.tax_withholding_category = source.tax_withholding_category

        # Get the advance paid Journal Entries in Purchase Invoice Advance
        if target.get("allocate_advances_automatically"):
            target.set_advances()

        target.set_payment_schedule()
        target.credit_to = get_party_account("Supplier", source.supplier, source.company)

    def update_item(obj, target, source_parent):
        target.amount = flt(obj.amount) - flt(obj.billed_amt)
        target.base_amount = target.amount * flt(source_parent.conversion_rate)
        target.qty = (
            target.amount / flt(obj.rate) if (flt(obj.rate) and flt(obj.billed_amt)) else flt(obj.qty)
        )

        item = get_item_defaults(target.item_code, source_parent.company)
        item_group = get_item_group_defaults(target.item_code, source_parent.company)
        target.cost_center = (
            obj.cost_center
            or frappe.db.get_value("Project", obj.project, "cost_center")
            or item.get("buying_cost_center")
            or item_group.get("buying_cost_center")
        )

    fields = {
        "Purchase Order": {
            "doctype": "Purchase Invoice",
            "field_map": {
                "party_account_currency": "party_account_currency",
                "supplier_warehouse": "supplier_warehouse",
                "custom_grand_total": "custom_grand_total",
                "custom_tax_rate": "custom_tax_rate",
            },
            "field_no_map": ["payment_terms_template"],
            "validation": {
                "docstatus": ["=", 1],
            },
        },
        "Purchase Order Item": {
            "doctype": "Purchase Invoice Item",
            "field_map": {
                "name": "po_detail",
                "parent": "purchase_order",
                "material_request": "material_request",
                "material_request_item": "material_request_item",
                "wip_composite_asset": "wip_composite_asset",
            },
            "postprocess": update_item,
            "condition": lambda doc: (doc.base_amount == 0 or abs(doc.billed_amt) < abs(doc.amount)),
        },
        "Purchase Taxes and Charges": {"doctype": "Purchase Taxes and Charges", "reset_value": True},
    }

    doc = get_mapped_doc(
        "Purchase Order",
        source_name,
        fields,
        target_doc,
        postprocess,
        ignore_permissions=ignore_permissions,
    )

    return doc

import erpnext
erpnext.buying.doctype.purchase_order.purchase_order.get_mapped_purchase_invoice = get_mapped_purchase_invoice
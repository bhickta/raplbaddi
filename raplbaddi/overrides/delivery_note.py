import frappe

def before_insert(doc, method):
    set_naming_series(doc)

def set_naming_series(doc):
    naming_series_map = {
        "Real Appliances Private Limited": {
            False: "DN-.YY.-RAPL-.####",
            True: "DRET-.YY.-RAPL-.####"
        },
        "Red Star Unit 2": {
            False: "DN-.YY.-RSI-.####",
            True: "DRET-.YY.-RSI-.####"
        }
    }

    if doc.branch in naming_series_map:
        doc.naming_series = naming_series_map[doc.branch][False]

def validate(doc, method):
    validate_naming_series(doc)
    calculate_freight_amount(doc)

from raplbaddi.utils import make_fields_set_only_once
def validate_naming_series(doc):
    make_fields_set_only_once(doc, ["branch"])

def on_submit(doc, method):
    create_reverse_entry_for_internal_customers(doc)

def on_update_after_submit(doc, method):
    calculate_freight_amount(doc)

def create_reverse_entry_for_internal_customers(doc):
    internal_customers = ["Real Appliances Pvt Ltd (RAPL-Unit 1)"]
    if doc.customer not in internal_customers:
        return
    
    items_considered = [item for item in doc.items if item.item_group == "Geyser Unit"]

    if items_considered:
        stock_entry = {
            "doctype": "Stock Entry",
            "stock_entry_type": "Internal Receipt",
            "items": []
        }

        for item in items_considered:
            stock_entry["items"].append({
                "item_code": item.item_code,
                "qty": item.qty,
                "uom": item.uom,
                "t_warehouse": item.warehouse
            })
        internal_receipt = frappe.get_doc(stock_entry).insert().submit()
        doc.internal_receipt = internal_receipt.name
        doc.save()

def before_cancel(doc, method):
    doc.internal_receipt = None

def on_cancel(doc, method):
    cancel_reverse_entry_for_internal_customers(doc)

def cancel_reverse_entry_for_internal_customers(doc):
    if not doc.internal_receipt:
        return
    else:
        frappe.get_doc("Stock Entry", doc.internal_receipt).cancel()

def calculate_freight_amount(doc):
    if not frappe.user.has_role("Transportation Manager"):
        frappe.throw("You are not allowed to calculate freight amount, only Transportation Manager can do it.")
    doc.amount = 0
    for item in doc.freight:
        doc.amount += item.amount
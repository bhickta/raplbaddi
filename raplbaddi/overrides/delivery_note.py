import frappe


def before_insert(doc, method):
    set_naming_series(doc)


def set_naming_series(doc):
    naming_series_map = {
        "Real Appliances Private Limited": {
            False: "DN-.YY.-RAPL-.####",
            True: "DRET-.YY.-RAPL-.####",
        },
        "Red Star Unit 2": {False: "DN-.YY.-RSI-.####", True: "DRET-.YY.-RSI-.####"},
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
    is_internal_customer = frappe.get_cached_value(
        "Customer", doc.customer, "custom_is_internal_customer"
    )
    customer_group = frappe.get_cached_value("Customer", doc.customer, "customer_group")
    raplbaddi_settings = frappe.get_cached_doc("Raplbaddi Settings", "Raplbaddi Settings")
    sc_group = raplbaddi_settings.service_centre_group

    all_items_group = False
    if raplbaddi_settings.is_internal_receipt_for_service_centre_on_dn and customer_group in [sc_group,]:
        is_internal_customer = True
        all_items_group = True
    if not is_internal_customer:
        return

    if all_items_group:
        items_considered = doc.items
    else:
        items_considered = [
            item for item in doc.items if item.item_group == "Geyser Unit"
        ]

    if items_considered:
        stock_entry = {
            "doctype": "Stock Entry",
            "stock_entry_type": "Internal Receipt",
            "items": [],
        }

        for item in items_considered:
            stock_entry["items"].append(
                {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "uom": item.uom,
                    "t_warehouse": item.warehouse,
                }
            )
        internal_receipt = frappe.get_doc(stock_entry).insert().submit()
        doc.internal_receipt = internal_receipt.name
        doc.save()


def before_cancel(doc, method):
    doc.internal_receipt_name = doc.internal_receipt
    doc.internal_receipt = None


def on_cancel(doc, method):
    cancel_reverse_entry_for_internal_customers(doc)


def cancel_reverse_entry_for_internal_customers(doc):
    if not doc.internal_receipt_name:
        return
    else:
        frappe.get_doc("Stock Entry", doc.internal_receipt_name).cancel()


def calculate_freight_amount(doc):
    allowed_roles = {"Transportation Manager"}
    user_roles = set(frappe.get_roles(frappe.session.user))
    if not allowed_roles.intersection(user_roles):
        frappe.throw(
            f"You are not allowed to calculate freight amount. Only {', '.join(allowed_roles)} can do it."
        )

    doc.amount = 0
    for item in doc.freight:
        doc.amount += item.amount
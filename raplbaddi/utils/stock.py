import frappe


def make_manufacturing_stock_entry(**kwargs):
    items = kwargs.get("items")
    if not items:
        frappe.throw("Please provide items to make stock entry")
    stock_entry = {
        "doctype": "Stock Entry",
        "stock_entry_type": "Manufactured",
        "items": [],
    }
    doc = frappe.get_doc(stock_entry)

    for item in items:
        stock_entry["items"].append(
            {
                "item_code": item.item_code,
                "qty": item.qty,
                "t_warehouse": item.t_warehouse,
            }
        )
    internal_receipt = frappe.get_doc(stock_entry)
    internal_receipt.insert().submit()
    return internal_receipt.name
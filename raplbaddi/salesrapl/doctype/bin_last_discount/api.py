import frappe, ast

@frappe.whitelist()
def get_bin_details(args):
    args = ast.literal_eval(args)
    name = args.get("name")
    value = frappe.db.get_value(
        "Bin Last Discount",
        {
            "customer": args.get("customer"),
            "discount": args.get("discount"),
            "item": args.get("item"),
        },
        "name",
        as_dict=True,
    )
    if value:
        return value
    else:
        return None

@frappe.whitelist()
def update_discount(name, args):
    discount = args.get("discount")
    frappe.db.set_value(
        "Bin Last Discount",
        name,
        "discount",
        discount,
        update_modified=True,
    )

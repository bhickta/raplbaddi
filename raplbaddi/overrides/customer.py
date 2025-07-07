import frappe
from frappe.model.rename_doc import bulk_rename

def autoname(doc, method):
    naming = CustomerNaming(doc)
    doc.name = naming.generate_name()


def validate(doc, method):
    if doc.is_new():
        return
    old_doc = frappe.get_doc("Customer", doc.name)
    naming = CustomerNaming(doc)
    new_customer_group = doc.customer_group
    doc.db_update()
    if old_doc.customer_group != new_customer_group:
        frappe.rename_doc("Customer", doc.name, naming.generate_name())


class CustomerNaming:
    def __init__(self, doc):
        self.doc = doc

    def get_customer_group_abb(self):
        customer_group = frappe.get_doc("Customer Group", self.doc.customer_group)
        if not customer_group.abbreviation:
            customer_group.abbreviation = frappe.generate_hash(None, 3)
        return customer_group.abbreviation

    def get_name(self):
        abbreviation = self.get_customer_group_abb()
        base_name = f"P-{abbreviation}-"
        return self.get_latest_name(base_name)

    def get_latest_name(self, base_name):
        last_customer = frappe.get_all(
            "Customer",
            filters={"name": ["like", f"{base_name}%"]},
            fields=["name"],
            order_by="creation desc",
            limit_page_length=1,
        )
        next_count = 1
        if last_customer:
            last_customer = last_customer[0]
            next_count = int(last_customer.name.split("-")[-1]) + 1
            if next_count > 999:
                frappe.throw(
                    frappe._(
                        "Cannot create more than 999 customers with the same customer group."
                    )
                )
        return f"{base_name}{next_count}"

    def get_next_available_name(self, base_name):
        existing_customers = frappe.get_all(
            "Customer", filters={"name": ["like", f"{base_name}%"]}, fields=["name"]
        )
        existing_counts = [
            int(name.split("-")[-1])
            for name in [customer["name"] for customer in existing_customers]
            if name.split("-")[-1].isdigit()
        ]
        next_count = 1
        while next_count in existing_counts:
            next_count += 1
        return f"{base_name}{next_count}"

    def generate_name(self):
        return self.get_name()
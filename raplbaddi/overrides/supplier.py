import frappe
from frappe.model.rename_doc import bulk_rename

def autoname(doc, method):
    naming = SupplierNaming(doc)
    doc.name = naming.get_name()

def validate(doc, method):
    validate_party_code(doc)

def validate_party_code(doc):
    naming = SupplierNaming(doc)
    if not naming.party_code:
        return
    if doc.name != naming.party_code:
        frappe.rename_doc("Supplier", doc.name, naming.party_code)
        from erpnext.accounts.doctype.party_link.party_link import create_party_link
        create_party_link("Customer", naming.party_code, naming.party_code)
        

class SupplierNaming:
    def __init__(self, doc):
        self.doc = doc
        self.party_code = self.get_party_code_from_customer_having_sames_gstin()

    def get_party_code_from_customer_having_sames_gstin(self):
        gstin = self.doc.gstin
        if not gstin:
            return None
        party_code = frappe.get_all("Customer", filters={"gstin": gstin}, fields=["name"])
        if not party_code:
            return None
        return party_code[0].name
        
    def get_supplier_group_abb(self):
        supplier_group = frappe.get_doc("Supplier Group", self.doc.supplier_group)
        if not supplier_group.abbreviation:
            supplier_group.abbreviation = frappe.generate_hash(None, 3)
        return supplier_group.abbreviation

    def get_name(self):
        if self.doc.supplier_group == "Vehicle":
            return self.doc.supplier_name
        if self.party_code:
            return self.party_code
        abbreviation = self.get_supplier_group_abb()
        base_name = f"P-{abbreviation}-"
        return self.get_latest_name(base_name)

    def get_latest_name(self, base_name):
        last_supplier = frappe.get_all(
            "Supplier",
            filters={"name": ["like", f"{base_name}%"]},
            fields=["name"],
            order_by="creation desc",
            limit_page_length=1,
        )
        next_count = 1
        if last_supplier:
            last_supplier = last_supplier[0]
            next_count = int(last_supplier.name.split("-")[-1]) + 1
            if next_count > 999:
                frappe.throw(
                    frappe._(
                        "Cannot create more than 999 suppliers with the same supplier group."
                    )
                )
        return f"{base_name}{next_count}"

    def get_next_available_name(self, base_name):
        existing_suppliers = frappe.get_all(
            "Supplier", filters={"name": ["like", f"{base_name}%"]}, fields=["name"]
        )
        existing_counts = [
            int(name.split("-")[-1])
            for name in existing_suppliers
        ]
        next_count = 1
        while next_count in existing_counts:
            next_count += 1
        return f"{base_name}{next_count}"
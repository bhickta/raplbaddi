# /your_app/utils/party_manager.py

import frappe
# Import the standard ERPNext function as requested
from erpnext.accounts.doctype.party_link.party_link import create_party_link

class PartyManager:
    def __init__(self, doc):
        self.doc = doc
        self.doctype = doc.doctype
        self.gstin = doc.get("gstin")

    # This is the updated method
    def sync_party_link(self):
        """
        Calls the standard ERPNext function to create a Party Link.
        This function handles all the internal logic of checking for
        a counterpart and creating the link if it doesn't exist.
        """
        # The function takes the doctype and name of the current party.
        # It will automatically look for the counterpart with the same name.
        create_party_link(self.doctype, self.doc.name)

    # --- NO OTHER CHANGES ARE NEEDED BELOW THIS LINE ---

    def validate_gstin_uniqueness_per_doctype(self):
        """
        Ensures that a given GSTIN is unique for that specific Doctype.
        """
        if not self.gstin:
            return

        existing_doc = frappe.db.exists(self.doctype, {
            "gstin": self.gstin,
            "name": ["!=", self.doc.name]
        })

        if existing_doc:
            frappe.throw(
                (f"Another {self.doctype} with GSTIN {frappe.bold(self.gstin)} already exists: "
                 f"<a href='/app/{self.doctype.lower().replace(' ', '-')}/{existing_doc}' class='strong'>"
                 f"{existing_doc}</a>."),
                title=f"Duplicate {self.doctype}"
            )

    def get_name(self):
        """Determines the correct name for a new document."""
        if self.doctype == "Supplier" and self.doc.supplier_group == "Vehicle":
            return self.doc.supplier_name
        if self.gstin:
            existing_name = self._find_party_by_gstin()
            if existing_name:
                return existing_name
        return self._generate_new_series_name()

    def sync_name_on_update(self):
        """Synchronizes the name on document updates."""
        if self.doc.is_new() or not self.gstin:
            return
            
        existing_name = self._find_party_by_gstin(include_self=False)
        
        if existing_name and self.doc.name != existing_name:
            frappe.rename_doc(self.doctype, self.doc.name, existing_name, ignore_permissions=True)
            frappe.msgprint(f"Renamed to {frappe.bold(existing_name)} to match party with the same GSTIN.", title="Name Synchronized", indicator="green")
            self.doc.reload()

    def _find_party_by_gstin(self, include_self=True):
        """Finds any Customer or Supplier with the same GSTIN."""
        if not self.gstin: return None
        for dt in ["Customer", "Supplier"]:
            filters = {"gstin": self.gstin}
            if not include_self:
                # This logic is slightly different from the uniqueness check,
                # as it's used for finding a name to adopt.
                if self.doc.name:
                    filters["name"] = ("!=", self.doc.name)
            
            party_name = frappe.db.get_value(dt, filters, "name")
            if party_name: return party_name
        return None

    def _generate_new_series_name(self):
        """Generates a new name (e.g., P-ABC-1), ensuring it's unique across both doctypes."""
        if self.doctype == "Customer":
            group_name, abbr_field, group_doctype = self.doc.customer_group, "abbreviation", "Customer Group"
        elif self.doctype == "Supplier":
            group_name, abbr_field, group_doctype = self.doc.supplier_group, "abbreviation", "Supplier Group"
        else:
            return self.doc.name
        
        abbreviation = frappe.db.get_value(group_doctype, group_name, abbr_field)
        if not abbreviation: abbreviation = frappe.generate_hash(length=3).upper()
        
        base_name = f"P-{abbreviation}-"
        
        customer_names = frappe.get_all("Customer", filters={"name": ["like", f"{base_name}%"]}, pluck="name")
        supplier_names = frappe.get_all("Supplier", filters={"name": ["like", f"{base_name}%"]}, pluck="name")
        
        max_count = 0
        for name in customer_names + supplier_names:
            try:
                count = int(name.split("-")[-1])
                if count > max_count: max_count = count
            except (ValueError, IndexError): continue
        
        next_count = max_count + 1
        if next_count > 999: frappe.throw(f"Series limit reached for prefix {base_name}")
        return f"{base_name}{next_count}"
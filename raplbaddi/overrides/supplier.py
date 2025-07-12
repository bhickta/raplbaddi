# supplier.py

import frappe
from .party_manager import PartyManager

def autoname(doc, method):
    manager = PartyManager(doc)
    doc.name = manager.get_name()

def validate(doc, method):
    manager = PartyManager(doc)
    
    # Step 1: Strictly enforce that only one Supplier can have this GSTIN.
    manager.validate_gstin_uniqueness_per_doctype()

    # Step 2: Handle name unification if a Customer is added/updated.
    manager.sync_name_on_update()

    # Step 3: Create the link between the Customer and Supplier.
    # manager.sync_party_link()
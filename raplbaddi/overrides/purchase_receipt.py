from .delivery_note import set_naming_series, calculate_freight_amount
from raplbaddi.utils.accounts import create_journal_entry

def before_insert(doc, method):
    set_naming_series(doc)

def set_naming_series(doc):
    naming_series_map = {
        "Real Appliances Private Limited": {
            False: "PR-.YY.-RAPL-.####",
        },
        "Red Star Unit 2": {
            False: "PR-.YY.-RSI-.####",
        }
    }

    if doc.branch in naming_series_map:
        doc.naming_series = naming_series_map[doc.branch][False]

from erpnext.stock.doctype.purchase_receipt.purchase_receipt import PurchaseReceipt
from frappe.model.document import frappe, msgprint
from frappe.utils.dateutils import get_datetime

def validate(doc, method):
    posting_datetime_same_as_creation(doc)
    calculate_freight_amount(doc)

def on_submit(doc, method):
    pass

def on_update_after_submit(doc, method):
    if doc.workflow_state == "Audited":
        create_purchase_invoice(doc, method)
        raplbaddi_settings = frappe.get_cached_doc("Raplbaddi Settings", "Raplbaddi Settings")
        if raplbaddi_settings.is_create_journal_entry_for_transportation:
            create_journal_entry(
                source_doc=doc,
                acc1="Inward Freight Expense - RAPL",
                acc2="Creditors - RAPL",
                party_type="Supplier", party=doc.custom_vehicle_no, 
                acc1_amount=doc.amount, acc2_amount=doc.amount,
                submit=True,
            )

def posting_datetime_same_as_creation(doc):
    return
    creation_date = get_datetime(doc.creation)
    doc.posting_date = creation_date.date()
    doc.posting_time = creation_date.time()
    doc.set_posting_time = 1

class PurchaseReceipt(PurchaseReceipt):
    
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

from .delivery_note import InvoiceAutomation
def create_purchase_invoice(doc, method):
    raplbaddi_settings = frappe.get_cached_doc("Raplbaddi Settings", "Raplbaddi Settings")
    if not raplbaddi_settings.is_create_purchase_invoice_via_purchase_receipt:
        return
    submit = "submit" if raplbaddi_settings.is_submit_purchase_invoice else None
    InvoiceAutomation(doc, mode=submit).process()
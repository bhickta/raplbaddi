from .delivery_note import set_naming_series

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
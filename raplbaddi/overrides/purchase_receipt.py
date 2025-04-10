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

from erpnext.stock.doctype.purchase_receipt.purchase_receipt import get_returned_qty_map, _, get_invoiced_qty_map, merge_taxes, flt, get_mapped_doc
@frappe.whitelist()
def make_purchase_invoice(source_name, target_doc=None, args=None):
	from erpnext.accounts.party import get_payment_terms_template

	doc = frappe.get_doc("Purchase Receipt", source_name)
	returned_qty_map = get_returned_qty_map(source_name)
	invoiced_qty_map = get_invoiced_qty_map(source_name)

	def set_missing_values(source, target):
		if len(target.get("items")) == 0:
			frappe.throw(_("All items have already been Invoiced/Returned"))

		doc = frappe.get_doc(target)
		doc.payment_terms_template = get_payment_terms_template(source.supplier, "Supplier", source.company)
		doc.run_method("onload")
		doc.run_method("set_missing_values")

		if args and args.get("merge_taxes"):
			merge_taxes(source.get("taxes") or [], doc)

		doc.run_method("calculate_taxes_and_totals")
		doc.set_payment_schedule()

	def update_item(source_doc, target_doc, source_parent):
		target_doc.qty, returned_qty = get_pending_qty(source_doc)
		if frappe.db.get_single_value("Buying Settings", "bill_for_rejected_quantity_in_purchase_invoice"):
			target_doc.rejected_qty = 0
		target_doc.stock_qty = flt(target_doc.qty) * flt(
			target_doc.conversion_factor, target_doc.precision("conversion_factor")
		)
		returned_qty_map[source_doc.name] = returned_qty

	def get_pending_qty(item_row):
		qty = item_row.qty
		if frappe.db.get_single_value("Buying Settings", "bill_for_rejected_quantity_in_purchase_invoice"):
			qty = item_row.received_qty

		pending_qty = qty - invoiced_qty_map.get(item_row.name, 0)

		if frappe.db.get_single_value("Buying Settings", "bill_for_rejected_quantity_in_purchase_invoice"):
			return pending_qty, 0

		returned_qty = flt(returned_qty_map.get(item_row.name, 0))
		if item_row.rejected_qty and returned_qty:
			returned_qty -= item_row.rejected_qty

		if returned_qty:
			if returned_qty >= pending_qty:
				pending_qty = 0
				returned_qty -= pending_qty
			else:
				pending_qty -= returned_qty
				returned_qty = 0

		return pending_qty, returned_qty

	doclist = get_mapped_doc(
		"Purchase Receipt",
		source_name,
		{
			"Purchase Receipt": {
				"doctype": "Purchase Invoice",
				"field_map": {
					"supplier_warehouse": "supplier_warehouse",
					"is_return": "is_return",
					"bill_date": "bill_date",
					"custom_grand_total": "custom_grand_total",
					"custom_tax_rate": "custom_tax_rate",
				},
				"validation": {
					"docstatus": ["=", 1],
				},
			},
			"Purchase Receipt Item": {
				"doctype": "Purchase Invoice Item",
				"field_map": {
					"name": "pr_detail",
					"parent": "purchase_receipt",
					"qty": "received_qty",
					"purchase_order_item": "po_detail",
					"purchase_order": "purchase_order",
					"is_fixed_asset": "is_fixed_asset",
					"asset_location": "asset_location",
					"asset_category": "asset_category",
					"wip_composite_asset": "wip_composite_asset",
				},
				"postprocess": update_item,
				"filter": lambda d: get_pending_qty(d)[0] <= 0
				if not doc.get("is_return")
				else get_pending_qty(d)[0] > 0,
			},
			"Purchase Taxes and Charges": {
				"doctype": "Purchase Taxes and Charges",
				"reset_value": not (args and args.get("merge_taxes")),
				"ignore": args.get("merge_taxes") if args else 0,
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist
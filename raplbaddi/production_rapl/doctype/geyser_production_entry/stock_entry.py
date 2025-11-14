import frappe
from frappe.model.document import Document
import erpnext

if TYPE_CHECKING:
	from erpnext.stock.doctype.stock_entry.stock_entry import StockEntry




@frappe.whitelist()
def make_stock_entry(**args):
	"""Helper function to make a Stock Entry

	:item_code: Item to be moved
	:qty: Qty to be moved
	:company: Company Name (optional)
	:from_warehouse: Optional
	:to_warehouse: Optional
	:rate: Optional
	:serial_no: Optional
	:batch_no: Optional
	:posting_date: Optional
	:posting_time: Optional
	:purpose: Optional
	:do_not_save: Optional flag
	:do_not_submit: Optional flag
	"""
	

	s = frappe.new_doc("Stock Entry")
	args = frappe._dict(args)
	s.company = args.company or erpnext.get_default_company()
	
	# items
	for item in args.items:
		s.append('items', {
			"item_code": item['item_code'],
			"t_warehouse": item['to_warehouse'],
			"qty": item['qty']
		})

	# insert
	s.insert()
	s.submit()
	return s
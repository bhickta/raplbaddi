from erpnext.stock.doctype.stock_reconciliation.stock_reconciliation import StockReconciliation as _StockReconciliation
import frappe

class StockReconciliation(_StockReconciliation):
	def submit(self):
		if len(self.items) > 1000:
			frappe.msgprint(
				(
					"The task has been enqueued as a background job. In case there is any issue on processing in background, the system will add a comment about the error on this Stock Reconciliation and revert to the Draft stage"
				)
			)
			self.queue_action("submit", timeout=4600)
		else:
			self._submit()
frappe.ui.form.on("Purchase Order", {
  onload: function (frm) {
    // if (frm.doc.docstatus == 0) {
    //   frm.toggle_reqd("supplier", false);
    // }
  },
  refresh: function (frm) {
    frm.events.queries(frm);
    frm.events.make_date_and_time_not_change_on_change(frm);
  },
  queries(frm) {
    frm.set_query("billing_rule", function () {
      return {
        query: "raplbaddi.controllers.queries.billing_rule",
        filters: {
          applicable_for: ["in", ["Buying", "Both"]],
        },
      };
    });
  },

  make_date_and_time_not_change_on_change: function (frm) {
    frm.toggle_display("set_posting_time", false)
  },
});


class rbPurchaseOrderController extends erpnext.buying.PurchaseOrderController {
	make_purchase_receipt() {
		frappe.model.open_mapped_doc({
			method: "raplbaddi.overrides.purchase_order.make_purchase_receipt",
			frm: cur_frm,
			freeze_message: __("Creating Purchase Receipt ..."),
		});
	}

	make_purchase_invoice() {
		frappe.model.open_mapped_doc({
			method: "raplbaddi.overrides.purchase_order.make_purchase_invoice",
			frm: cur_frm,
		});
	}
}


extend_cscript(cur_frm.cscript, new rbPurchaseOrderController({ frm: cur_frm }));
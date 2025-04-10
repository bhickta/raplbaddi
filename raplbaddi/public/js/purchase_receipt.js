frappe.ui.form.on("Purchase Receipt", {
  onload: function (frm) {
    if (frm.doc.docstatus == 0) {
      frm.toggle_reqd("supplier", false);
    }
  },

  refresh: function (frm) {
    frm.events.make_date_and_time_not_change_on_change(frm);
    frm.events.add_queries(frm);
  },

  add_queries: function (frm) {
    frm.events.custom_vehicle_no_query(frm);
  },

  custom_vehicle_no_query: function (frm) {
    frm.set_query("custom_vehicle_no", function () {
      return {
        filters: {
          supplier_group: "Vehicle",
        }
      };
    });
  },

  make_date_and_time_not_change_on_change: function (frm) {
    frm.toggle_display("set_posting_time", false)
  },
  supplier: function (frm) {
    frm.events.set_values_for_service_centre_supplier(frm)
  },

  set_values_for_service_centre_supplier(frm) {
    frm.call({
      method: "raplbaddi.supportrapl.doctype.service_centre.service_centre.get_service_centre_details",
      args: {
        "filters": {
          supplier: frm.doc.supplier
        }
      },
      callback: function (r) {
      }
    })
  }

});


class rbPurchaseReceiptController extends erpnext.stock.PurchaseReceiptController {
	make_purchase_invoice() {
		frappe.model.open_mapped_doc({
			method: "raplbaddi.overrides.purchase_receipt.make_purchase_invoice",
			frm: cur_frm,
		});
	}
}


extend_cscript(cur_frm.cscript, new rbPurchaseReceiptController({ frm: cur_frm }));
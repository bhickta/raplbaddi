frappe.ui.form.on("Purchase Receipt", {
  onload: function (frm) {
    if (frm.doc.docstatus == 0) {
      frm.toggle_reqd("supplier", false);
    }
  },

  refresh: function (frm) {
    frm.events.make_date_and_time_not_change_on_change(frm);
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
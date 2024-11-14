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
});
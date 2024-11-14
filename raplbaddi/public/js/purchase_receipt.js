frappe.ui.form.on("Purchase Receipt", {
  onload: function (frm) {
    if (frm.doc.docstatus == 0) {
      frm.toggle_reqd("supplier", false);
    }
  },
});
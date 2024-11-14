frappe.ui.form.on("Purchase Order", {
  onload: function (frm) {
    // if (frm.doc.docstatus == 0) {
    //   frm.toggle_reqd("supplier", false);
    // }
  },
  refresh: function (frm) {
    frm.events.queries(frm);
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
});
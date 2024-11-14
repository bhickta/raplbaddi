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
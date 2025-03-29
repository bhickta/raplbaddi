frappe.ui.form.on("Delivery Note", {
    refresh: function (frm) {
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
    }
});
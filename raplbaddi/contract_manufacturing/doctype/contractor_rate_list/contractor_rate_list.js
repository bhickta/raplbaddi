// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.ui.form.on("Contractor Rate List", {
    onload(frm) {

    },
	refresh(frm) {
        frm.events.set_queries(frm);
	},
    set_queries(frm) {
        console.log("set_queries");
        frm.set_query("item_code", "items", function() {
            return {
                filters: {
                    "is_contractable": 1
                }
            }
        }
        );
    }
});

// Copyright (c) 2024, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Salary", {
    onload(frm) {
        if(frm.doc.__islocal) {
            frm.events.fill_months(frm)
        }
    },
    fill_months(frm) {
                // Define all months
                const months = [
                    "January", "February", "March", "April",
                    "May", "June", "July", "August",
                    "September", "October", "November", "December"
                ];
                
                // Create a set of existing months for quick lookup
                const existingMonths = new Set(frm.doc.items.map(item => item.month));
                
                // Loop through the months and add any missing months
                months.forEach(month => {
                    if (!existingMonths.has(month)) {
                        frm.add_child("items", {
                            month: month // Adjust the field name if necessary
                        });
                    }
                });
        
                frm.refresh_field("items");
    }
});

frappe.ui.form.on("Month Item", {
    value(frm, cdt, cdn) {
        let d = locals[cdt][cdn]
        let cl = frm.doc.items
        let currentIndex = cl.findIndex(item => item.name === d.name);
        
        for (let i = currentIndex + 1; i < cl.length; i++) {
            cl[i].value = d.value;
        }

        frm.refresh_field('items');
    }
});


cur_frm.cscript.value = function (doc, cdt, cdn) {
	erpnext.utils.copy_value_in_all_rows(doc, cdt, cdn, "items", "value");
};
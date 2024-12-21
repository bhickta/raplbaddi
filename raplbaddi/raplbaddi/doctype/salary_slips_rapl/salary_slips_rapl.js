// Copyright (c) 2024, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.ui.form.on("Salary Slips Rapl", {
    department: function(frm) {
        fill_items_onload(frm);
    },
    branch: function(frm) {
        fill_items_onload(frm);
    },
    employee: function(frm) {
        fill_items_onload(frm);
    }
});

function fill_items_onload(frm) {
    if(!cur_frm.doc.__unsaved) {
        return
    }
    frappe.call({
        method: 'raplbaddi.raplbaddi.doctype.attendance_rapl.attendance_rapl.get_employee_shift_info',
        frm: frm,
        args: {
            doc: frm.doc,
        },
        callback: function(response) {
            if (response.message) {
                frm.clear_table('items');
                response.message.forEach(info => {
                    const row = frm.add_child('items');
                    row.employee = info.employee;
                });
                frm.refresh_field('items');
            }
        }
    });
}
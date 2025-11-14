// Copyright (c) 2024, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.ui.form.on("User Access Control", {
	refresh(frm) {

	},
    user(frm) {
        frm.events.populate_uac_table(frm)
    },
    async populate_uac_table(frm) {
        frm.clear_table('items')
        let args = {
            user: frm.doc.user,
        }
        let response = await frm.call({
            doc: frm.doc,
            method: 'get_user_permissions',
            args
        })
        let user_permission = response?.message
        if(!user_permission) {return}
        user_permission.forEach(permission => {
            frm.add_child("items", permission);
        })
        frm.refresh_field("items")
    }
});

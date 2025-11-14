// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.ui.form.on('Serial No Changing Entry', {
	onload(frm) {
		frm.set_query("geyser", function () {
			return {
				"filters": {
					"item_group": "Geyser Unit",
				}
			};
		});
	},
	before_save(frm){
		frm.set_value('qty', frm.doc.items.length)
	},
	populate(frm){
		let doc = frm.doc
		if(doc.from_serial && doc.to_serial){
			for (let i = doc.from_serial; i <= doc.to_serial; i++) {
				console.log("object");
				frm.add_child('items', {serial_number: i})
				frm.refresh_field('items')
			}
		}
	}
});

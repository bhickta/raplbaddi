// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.ui.form.on('Geyser Brand Changing Entry', {
	onload(frm) {
		frm.set_query("item", "items", function () {
			return {
				"filters": {
					"item_group": "Geyser Unit",
					"disabled": 0
				}
			};
		});
	},
	before_save(frm) {
		let total = 0
		frm.doc.items.forEach(
			(item) => {
				total = total + item.qty
			}
		)
		console.log(total);
		frm.set_value('total', total)
	}
});

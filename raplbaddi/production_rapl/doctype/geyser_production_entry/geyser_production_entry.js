// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.ui.form.on('Geyser Production Entry', {
	onload(frm) {
		frm.set_query("item", "items", function () {
			return frm.events.get_items_filters(frm)
		});
		frm.set_query("item_group", function () {
			return {
				"filters": {
					"name": ["in", ["Geyser Unit", "Cooler"]],
				}
			}
		})
	},
	get_items_filters(frm) {
		let default_filters = {
			"filters": {
				"item_group": ["in", ["Geyser Unit", "Cooler"]],
			}
		};
		if (frm.doc.item_group) {
			default_filters.filters.item_group = frm.doc.item_group;
		}
		return default_filters
	},
	before_save(frm) {
		let total = 0
		frm.doc.items.forEach(
			(item) => {
				total = total + item.qty
			}
		)
		frm.set_value('total', total)
	}
});

frappe.ui.form.on('Geyser Production Entry Table', {
	to_serial(frm, cdt, cdn) {
		calculate_qty(frm, cdt, cdn)
	}
});

function calculate_qty(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	if (row.to_serial - row.from_serial + 1) {
		frappe.model.set_value(cdt, cdn, 'qty', row.to_serial - row.from_serial + 1);
	} else {
		frappe.throw("Qty should be 1 or Above")
		frappe.model.set_value(cdt, cdn, 'qty', 0);
	}
	if (!(row.qty > 0)) {
		frappe.throw("Qty should be 1 or Above")
		frappe.model.set_value(cdt, cdn, 'qty', 0);

	}
}
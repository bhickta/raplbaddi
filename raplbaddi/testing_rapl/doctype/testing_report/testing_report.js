// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt
frappe.ui.form.on('Testing Report', {
	onload(frm) {
		frm.get_field("items").grid.cannot_add_rows = true;
		frm.get_field("items").grid.cannot_delete_rows = true;
		frm.set_query("department", function (doc) {
			return {
				filters: {
					parent_department: "Testing - RAPL"
				}
			};
		});
	},
	fetch_parameters(frm) {
		fetch_parameters(frm)
	},
	department(frm) {
		let department_map = {
			"Element : T - RAPL": "Element Unit",
			"Tank: T - RAPL": "Tank Metal",
			"Paintshop : T - RAPL": "Geyser Unit",
		};

		// frappe.db.get_value('Department', frm.doc.department, 'has_standard_testing').then(r => {
		// 	let hasStandardTesting = r.message.has_standard_testing
		// 	if (hasStandardTesting) {
		// 		frm.add_child('items', { item_type: 'Item' })
		// 	} else {
		// 		frm.add_child('items', { item_type: 'Non Standard Testing Report Item' })
		// 	}
		// 	frm.refresh_field('items')
		// })

		let department = frm.doc.department;
		let itemGroup = department_map[department] || "";

		frm.set_query("item", function (doc) {
			return {
				filters: {
					item_group: itemGroup
				}
			};
		});
	}
});

function fetch_parameters(frm) {
	frappe.db.get_value('Department', frm.doc.department, 'abbriviation').then(r => {
		let abb = r.message.abbriviation
		console.log(abb);
		frappe.db.get_list('Testing Parameters').then(
			r => {
				r.forEach(i => {
					if (i.name.includes(abb)) {
						console.log(i.name);
						frm.add_child('items', {
							parameter: i.name,
							qty_tested: frm.doc.qty_tested,
							item: frm.doc.item,
							item_name: frm.doc.item_name,
							item_type: 'Item'
						})
					}
				})
				frm.refresh_field('items')
			}
		)
	})
}
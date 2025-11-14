// Copyright (c) 2023, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.ui.form.on('Paper Name', {
	add_supplier(frm) {
		frm.doc.items.forEach(i => {
			frm.add_child('priority_and_rates', { 'supplier': frm.doc.supplier, 'priority': frm.doc.priority, 'paper': i.name, 'model': i.model, 'capacity': i.capacity })
		})
		frm.refresh_field('priority_and_rates')
	}
});
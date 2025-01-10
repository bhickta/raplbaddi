for(doctype of ["Customer", "Supplier"]) {
	add_name_to_doctype_links(doctype);
}

function add_name_to_doctype_links(doctype) {
	frappe.form.link_formatters[doctype] = function (value, doc) {
		let doctype_slug = doctype.toLowerCase();
		let customer_name = doc[doctype_slug + "_name"] || doc.party_name;
		let customer = doc[doctype_slug] || doc.party;
		if (doc && value && customer_name && customer_name !== value && customer === value) {
			return value + ": " + customer_name;
		} else if (!value && doc.doctype && customer_name) {
			// format blank value in child table
			return customer_name;
		} else {
			return value;
		}
	};
}
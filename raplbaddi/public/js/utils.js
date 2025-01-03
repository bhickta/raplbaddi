frappe.form.link_formatters["Customer"] = function (value, doc) {
	if (doc && value && doc.customer_name && doc.customer_name !== value && doc.customer === value) {
		return value + ": " + doc.customer_name;
	} else if (!value && doc.doctype && doc.customer_name) {
		// format blank value in child table
		return doc.customer_name;
	} else {
		return value;
	}
};
console.log("HHehheh")
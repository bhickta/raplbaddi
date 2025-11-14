frappe.pages["crp"].on_page_load = function (wrapper) {
	frappe.ui.make_app_page({
		parent: wrapper,
		title: __("CRP"),
		single_column: true,
	});
};

frappe.pages["crp"].on_page_show = function (wrapper) {
	load_desk_page(wrapper);
};

function load_desk_page(wrapper) {
	let $parent = $(wrapper).find(".layout-main-section");
	$parent.empty();

	frappe.require("crp.bundle.js").then(() => {
		frappe.crp = new frappe.ui.Crp({
			wrapper: $parent,
			page: wrapper.page,
		});
	});
}
// Copyright (c) 2024, Nishant Bhickta and contributors
// For license information, please see license.txt

frappe.ui.form.on("Brand Specification", {
    refresh(frm) {
        frm.events.hide_set_aliases(frm)
    },
    populate_alias(frm) {
        frm.call({
            method: "populate_alias",
            doc: frm.doc,
            callback: (r) => {
                console.log(r.message)
            }
        })
    },
    hide_set_aliases(frm) {
        if (frm.doc.brand_aliases.length > 0) {
            frm.fields_dict.populate_alias.toggle(false)
            frm.fields_dict.default_alias.toggle(false)
        }
    },
    populate_stickers(frm) {
        if (frm.doc.stickers) {
            frappe.call({
                method: "populate_stickers",
                doc: frm.doc,
                callback: (r) => {
                    console.log(r.message)
                }
            })
        }
    }
});
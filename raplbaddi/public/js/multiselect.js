frappe.provide("raplbaddi");

/**
 * A robust, self-contained multi-select dialog for child tables.
 * It reads existing values from a source field, returns the new selection,
 * and ensures the table always has at least one row to start.
 *
 * @class GenericMultiSelectDialog
 * @param {object} opts - Options for the dialog.
 * @param {object} opts.frm - The main form object.
 * @param {string} opts.cdt - The child doctype name (e.g., 'Sales Invoice Item').
 * @param {string} opts.cdn - The child doc name (the unique ID of the row).
 * @param {string} opts.source_fieldname - The fieldname in the child table that holds the comma-separated values.
 * @param {string} opts.target_doctype - The DocType to select from (e.g., 'Project').
 * @param {object} [opts.filters={}] - Filters to apply to the Link field query.
 * @param {function} opts.callback - The function to call with the array of selected values.
 */
class GenericMultiSelectDialog {
    constructor(opts) {
        this.frm = opts.frm;
        this.cdt = opts.cdt;
        this.cdn = opts.cdn;
        this.source_fieldname = opts.source_fieldname;
        this.target_doctype = opts.target_doctype;
        this.filters = opts.filters || {};
        this.callback = opts.callback;

        this.read_existing_values();
        this.make_dialog();
    }

    read_existing_values() {
        const row = locals[this.cdt][this.cdn];
        const source_value = row[this.source_fieldname] || '';
        this.existing_values = source_value ? source_value.split(/\s*,\s*/).filter(d => d) : [];
    }

    make_dialog() {
        this.dialog = new frappe.ui.Dialog({
            title: __("Select {0}", [this.target_doctype]),
            size: "large",
            fields: this.get_dialog_fields(),
            primary_action_label: __("Update"),
            primary_action: () => this.on_update(),
            on_page_show: () => {
                this.render_existing_data();
            }
        });
        this.dialog.show();
    }

    get_dialog_fields() {
        return [{
            fieldname: "selection_table",
            fieldtype: "Table",
            label: __("Select Entries"),
            fields: [{
                fieldname: "selection_entry",
                fieldtype: "Link",
                options: this.target_doctype,
                label: this.target_doctype,
                in_list_view: 1,
                get_query: () => ({ filters: this.filters }),
            }],
        }];
    }

    render_existing_data() {
        const table = this.dialog.get_field("selection_table");
        const data = this.existing_values.map(val => ({ "selection_entry": val }));
        table.df.data = data;
        if (table.df.data.length === 0) {
            table.df.data.push({});
        }
        table.grid.refresh();
    }

    on_update() {
        const table_data = this.dialog.get_field("selection_table").get_value();
        const selected_values = table_data
            .map(row => row.selection_entry)
            .filter(val => val);

        if (this.callback) {
            this.callback(selected_values);
        }

        this.dialog.hide();
    }
}

raplbaddi.GenericMultiSelectDialog = GenericMultiSelectDialog;
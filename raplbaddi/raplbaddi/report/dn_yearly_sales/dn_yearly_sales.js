frappe.query_reports["DN Yearly Sales"] = {

    filters: [],   // remove default filters

    onload: function (report) {

        // ---------------- ADD ITEM GROUP DROPDOWN ON TOP TOOLBAR ----------------
        report.page.add_field({
            fieldname: "item_group",
            label: "Item Group",
            fieldtype: "Link",
            options: "Item Group",
            default: "",
            onchange: function() {
                report.refresh();  // refresh report on selection
            }
        });

        // ---------------- VIEW BY CUSTOMER GROUP BUTTON ----------------
        report.page.add_inner_button("View by Customer Group", function () {

            let data = frappe.query_report.data;

            if (!data || data.length === 0) {
                frappe.msgprint("No data found to group.");
                return;
            }

            // Group by customer group
            let grouped = {};

            data.forEach(row => {
                let group = row["customer_group"] || "No Group";
                if (!grouped[group]) grouped[group] = [];
                grouped[group].push(row);
            });

            let final_output = [];

            Object.keys(grouped).forEach(group => {
                // header row
                final_output.push({
                    customer_name: "► " + group,
                    customer_group: "",
                    fy_24_25: "",
                    fy_25_26: ""
                });

                // rows
                grouped[group].forEach(r => final_output.push(r));
            });

            frappe.query_report.data = final_output;
            frappe.query_report.raw_data = final_output;
            report.refresh();

            frappe.msgprint("Grouped by Customer Group.");
        });

    }
};

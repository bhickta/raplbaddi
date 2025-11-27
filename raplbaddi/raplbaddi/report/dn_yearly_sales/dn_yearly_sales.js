frappe.query_reports["DN Yearly Sales"] = {

    filters: [
        {
            fieldname: "item_group",
            label: "Item Group",
            fieldtype: "Link",
            options: "Item Group"
        }
    ],

    onload: function (report) {

        // NO extra add_field needed now

        report.page.add_inner_button("View by Customer Group", function () {
            let data = frappe.query_report.data;

            if (!data || data.length === 0) {
                frappe.msgprint("No data found to group.");
                return;
            }

            // Grouping logic
            let grouped = {};
            data.forEach(row => {
                let group = row["customer_group"] || "No Group";
                if (!grouped[group]) grouped[group] = [];
                grouped[group].push(row);
            });

            let final_output = [];
            Object.keys(grouped).forEach(group => {
                final_output.push({
                    customer_name: "► " + group,
                    customer_group: "",
                    fy_24_25: "",
                    fy_25_26: ""
                });
                grouped[group].forEach(r => final_output.push(r));
            });

            frappe.query_report.data = final_output;
            frappe.query_report.raw_data = final_output;
            report.refresh();

            frappe.msgprint("Grouped by Customer Group.");
        });
    }
};

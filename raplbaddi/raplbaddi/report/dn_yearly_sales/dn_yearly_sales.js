frappe.query_reports["DN Yearly Sales"] = {
    onload: function (report) {

        // ------------------ CUSTOMER GROUP VIEW BUTTON ONLY ------------------
        report.page.add_inner_button("View by Customer Group", function () {

            let data = frappe.query_report.data;

            if (!data || data.length === 0) {
                frappe.msgprint("No data found to group.");
                return;
            }

            // Group client-side
            let grouped = {};

            data.forEach(row => {
                let group = row["customer_group"] || "No Group";

                if (!grouped[group]) {
                    grouped[group] = [];
                }

                grouped[group].push(row);
            });

            // Prepare grouped output
            let final_output = [];

            Object.keys(grouped).forEach(group => {
                // Group header row
                final_output.push({
                    customer_name: "► " + group,
                    customer_group: "",
                    fy_24_25: "",
                    fy_25_26: ""
                });

                // Add customer rows
                grouped[group].forEach(r => final_output.push(r));
            });

            // Replace report data with grouped result
            frappe.query_report.raw_data = final_output;
            frappe.query_report.data = final_output;

            // Refresh UI
            report.refresh();

            frappe.msgprint("Grouped by Customer Group.");
        });
    }
};

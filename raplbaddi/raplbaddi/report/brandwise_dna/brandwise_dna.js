frappe.query_reports["Brandwise_DNA"] = {
  "filters": [
    {
      fieldname: "from_date",
      label: "From Date",
      fieldtype: "Date",
      reqd: 1,
      default: frappe.datetime.add_days(frappe.datetime.get_today(), -30)
    },
    {
      fieldname: "to_date",
      label: "To Date",
      fieldtype: "Date",
      reqd: 1,
      default: frappe.datetime.get_today()
    },
    {
      fieldname: "item_group",
      label: "Item Group",
      fieldtype: "Link",
      options: "Item Group"
    },
    {
      fieldname: "brand",
      label: "Brand",
      fieldtype: "Link",
      options: "Brand"
    },
    {
      fieldname: "customer",
      label: "Customer",
      fieldtype: "Link",
      options: "Customer"
    },
    {
      fieldname: "status",
      label: "Status",
      fieldtype: "Select",
      options: ["", "Submitted", "Cancelled"],
      default: ""
    }
  ]
};

def get_columns(filters):
    columns = []

    if filters.group_by_sc:
        group_by_list = [
            {
                "fieldname": "service_centre",
                "label": ("Service Centre"),
                "fieldtype": "Link",
                "options": "Service Centre",
                "width": 170,
            },
             {
                "fieldname": "account_no",
                "label": ("Account No"),
                "fieldtype": "Data",    
                "width": 180,
            },
            {
                "fieldname": "bank",
                "label": ("Bank Name"),
                "fieldtype": "Data",
        
                "width": 170,
            },
            {
                "fieldname": "ifsc",
                "label": ("Bank IFSC"),
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "fieldname": "upi",
                "label": ("UPI Id"),
                "fieldtype": "Data",
                "width": 120,
            },
            {
                "fieldname": "count",
                "label": ("Complaints"),
                "fieldtype": "int",
                "width": 100,
            },
            {
                "fieldname": "kilometer",
                "label": ("Kilometers"),
                "fieldtype": "int",
                "width": 100,
            },
            {
                "fieldname": "amount",
                "label": ("Amount"),
                "fieldtype": "int",
                "width": 120,
            },
            {
                "fieldname": "per_complaint",
                "label": ("Per Complaint"),
                "fieldtype": "int",
                "width": 150,
            }
        ]
        columns.extend(group_by_list)

    if not filters.group_by_sc:
        ungrouped_list = [
            {
                "fieldname": "complaint_no",
                "label": ("Complaint No."),
                "fieldtype": "Link",
                "options": "IssueRapl",
                "width": 200,
            },
            {
                "fieldname": "date",
                "label": ("Date"),
                "fieldtype": "date",
                "width": 300,
            },
            {
                "fieldname": "service_centre",
                "label": ("Service Centre"),
                "fieldtype": "Link",
                "options": "Service Centre",
                "width": 300,
            },
            {
                "fieldname": "kilometer",
                "label": ("Kilometers"),
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "fieldname": "amount",
                "label": ("Amount"),
                "fieldtype": "int",
                "width": 150,
            },
            {
                "fieldname": "payment_status",
                "label": ("Payment Status"),
                "fieldtype": "int",
                "width": 150,
            },
            
        ]
        columns.extend(ungrouped_list)

    return columns


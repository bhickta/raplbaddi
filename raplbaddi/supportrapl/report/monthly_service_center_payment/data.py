def get_query(filters, conditions):
    group_by_query = f"""
        select 
            COUNT(i.name) as 'count',
            CASE WHEN i.custom_creation_date THEN DATE(i.custom_creation_date) ELSE DATE(i.creation) END as 'date',
            j.service_centre_name as 'service_centre',
            j.bank_name as 'bank',
            j.bank_account_no as 'account_no',
            j.ifsc_code as 'ifsc',
            j.upi_id as 'upi',
            sum(i.amount) as 'amount',
            i.payment_done as 'payment_done',
            i.service_delivered as 'service_delivered',
            sum(i.kilometer) as 'kilometer',
            i.customer_confirmation as 'customer_confirmation',
            i.payment_done as 'payment_status'
            
        from tabIssueRapl as i
            left Join
            `tabService Centre` as j on i.service_centre = j.service_centre_name
        where
            {conditions}
        group by
            i.service_centre
        order by
            amount DESC, count DESC
        """
    ungrouped_query = f"""
        select 
            1 as 'count',
            i.name as complaint_no,
            CASE WHEN i.custom_creation_date THEN DATE(i.custom_creation_date) ELSE DATE(i.creation) END as 'date',
            j.service_centre_name as 'service_centre',
            j.bank_name as 'bank',
            j.bank_account_no as 'account_no',
            j.ifsc_code as 'ifsc',
            j.upi_id as 'upi',
            i.amount as 'amount',
            i.payment_done as 'payment_status',
            i.service_delivered as 'service_delivered',
            i.customer_confirmation,
            i.kilometer as 'kilometer'

        from tabIssueRapl as i
            left Join
            `tabService Centre` as j on i.service_centre = j.service_centre_name
        where
            {conditions}
        order by
            amount DESC, count DESC
        """
        
    query = group_by_query if filters.group_by_sc else ungrouped_query
    print(query)
    return query



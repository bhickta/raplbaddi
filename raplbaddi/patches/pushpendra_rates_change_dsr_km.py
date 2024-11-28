import frappe

def execute():
    query = """
        UPDATE `tabDaily Sales Report By Admin` dsra
        SET
            dsra.amount_for_travel = dsra.km_travelled * 9,
            dsra.total_amount = dsra.total_amount + (dsra.km_travelled * 2)
        WHERE
            dsra.sales_person = 'Puspendra'
            and dsra.date > '2022-10-31'
    """
    frappe.db.sql(query)
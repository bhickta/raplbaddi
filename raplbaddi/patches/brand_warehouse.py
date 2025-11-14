import frappe


def execute():
    brands = frappe.get_all("Brand", fields=["brand"], pluck="brand")
    for brand in brands:
        warehouse = frappe.db.sql(f"""
            SELECT name FROM `tabWarehouse`
            where name like '%{brand}%'
            limit 1
        """)
        if warehouse:
            frappe.db.sql(f"""
                UPDATE `tabBrand`
                SET warehouse = '{warehouse[0][0]}'
                WHERE brand = '{brand}'
            """)
from frappe.query_builder import DocType
import frappe

class DSRA:
    def get_dsra(self):
        dsra = DocType('Daily Sales Report By Admin')
        query = (
            frappe.qb
            .from_(dsra)
            .select(dsra.date, dsra.sales_person, dsra.km_travelled, dsra.total_amount)
            .where(dsra.docstatus == 1)
            .where(dsra.sales_person != 'Dump')
        )
        return query.run(as_dict=True)
    
    def get_dsre(self):
        dsre = DocType('Daily Sales Expenses By Admin')
        query = (
            frappe.qb
            .from_(dsre)
            .select(dsre.parent,dsre.type, dsre.amount)
            .where(dsre.docstatus == 1)
        )
        return query.run(as_dict=True)
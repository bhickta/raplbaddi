# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SerialNoChangingEntry(Document):
    pass
#    def before_save(self):
#        date = self.get("date_of_entry")
#        transfer(date=date)


@frappe.whitelist()
def transfer(date):
    """Helper function to make a Stock Entry
    :items: Item to be moved
    """
    try:
        doc = frappe.get_doc('SNC Stock Entry', str(date))
        doc.append("items", {
            "t_warehouse": "Big Titan - RAPL",
            "f_warehouse": "Big Titan - RAPL",
            "qty": 10,
            "item_code": 'G3A',
        })
        doc.save()
        print(doc.items)
    except:
        doc = frappe.new_doc('SNC Stock Entry', str(date))
    finally:
        pass


@frappe.whitelist()
def get_production_data(serial_number):
    items = frappe.db.sql(f"""
		SELECT DISTINCT gpet.item_name, gpet.brand, gpe.date_of_production
		FROM `tabGeyser Production Entry Table` as gpet JOIN `tabGeyser Production Entry` as gpe ON gpe.name = gpet.parent
		WHERE '{serial_number}' BETWEEN from_serial AND to_serial
	""", as_dict=True)
    return items

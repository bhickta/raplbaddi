import frappe
from collections import Counter

class BaseReport:
    def __init__(self, filters):
        self.filters = filters or {}
        self.item_units = {}

    def get_city_from_shipping(self, shipping_address):
        return frappe.get_value("Address", shipping_address, "city")

    def get_ordered_box_qty(self, as_on_date=None):
        conditions = """
            po.docstatus = 1
            AND po.status NOT IN ('Stopped', 'Closed')
            AND poi.item_group = 'Packing Boxes'
        """
        
        # Add date filter only if as_on_date is given
        if as_on_date:
            conditions += f" AND po.transaction_date <= '{as_on_date}'"

        query = f"""
            SELECT
                poi.item_code, 
                SUM(GREATEST(poi.qty - poi.received_qty, 0)) AS ordered,
                po.supplier
            FROM
                `tabPurchase Order Item` poi
                JOIN `tabPurchase Order` po ON po.name = poi.parent
            WHERE
                {conditions}
            GROUP BY
                poi.item_code
        """
        result = frappe.db.sql(query, as_dict=True)
        return {
            r["item_code"]: {
                "ordered": r["ordered"], 
                "supplier": r["supplier"]
            } 
            for r in result
        }

    def set_item_unit(self, item_code):
        if item_code not in self.item_units:
            self.item_units[item_code] = frappe.get_cached_value("Item", item_code, "unit")
        return self.item_units[item_code]

    def count_cities(self, data):
        city_counts = Counter(row.get("city") for row in data)
        for row in data:
            row["city_count"] = city_counts[row.get("city")]

import frappe
import re


class StockMovementReport:
    def __init__(self, filters=None):
        self.filters = filters or {}
        self.columns = self.get_columns()
        self.data = []

    def get_columns(self):
        columns = [
            {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
            {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 150},
            {"label": "Stock Qty Current", "fieldname": "stock_qty", "fieldtype": "Float", "width": 100},
        ]
        for i in self.get_range_indices():
            from_date = self.filters.get(f"from_date_{i}")
            to_date = self.filters.get(f"to_date_{i}")
            date_range_label = f"{from_date} to {to_date}"
            columns.extend([
                {"label": f"DN Qty ({date_range_label})", "fieldname": f"dn_qty_{i}", "fieldtype": "Float", "width": 180},
                {"label": f"PR Qty ({date_range_label})", "fieldname": f"pr_qty_{i}", "fieldtype": "Float", "width": 180},
                {"label": f"SO Qty ({date_range_label})", "fieldname": f"so_qty_{i}", "fieldtype": "Float", "width": 180},
            ])
        return columns

    def get_range_indices(self):
        pattern = re.compile(r"from_date_(\d+)")
        return sorted(set(int(match.group(1)) for key in self.filters for match in [pattern.match(key)] if match))

    def fetch_items(self):
        conditions = []
        params = {}
        if self.filters.get("item_group"):
            conditions.append("i.item_group = %(item_group)s")
            params["item_group"] = self.filters.get("item_group")
        
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        
        return frappe.db.sql(f"""
            SELECT i.name AS item_code, i.item_name
            FROM `tabItem` i
            {where_clause}
        """, params, as_dict=1)

    def fetch_bin_data(self, item_codes):
        if not item_codes:
            return {}
        
        rows = frappe.db.sql("""
            SELECT bin.item_code, SUM(bin.actual_qty) AS actual_qty
            FROM `tabBin` bin
            WHERE bin.item_code IN %(item_codes)s
            GROUP BY bin.item_code
        """, {"item_codes": item_codes}, as_dict=1)
        
        return {row.item_code: row.actual_qty for row in rows}

    def fetch_qty_map(self, item_codes, doctype, child_table, item_field, date_field, from_date, to_date):
        if not item_codes:
            return {}

        rows = frappe.db.sql(f"""
            SELECT ct.{item_field} AS item_code, SUM(ct.qty) AS total_qty
            FROM `{child_table}` ct
            JOIN `{doctype}` dt ON dt.name = ct.parent
            WHERE ct.{item_field} IN %(item_codes)s
            AND dt.{date_field} BETWEEN %(from_date)s AND %(to_date)s
            AND dt.docstatus = 1
            GROUP BY ct.{item_field}
        """, {
            "item_codes": item_codes,
            "from_date": from_date,
            "to_date": to_date,
        }, as_dict=1)
        
        return {row.item_code: row.total_qty for row in rows}

    def build_data(self):
        items = self.fetch_items()
        if not items:
            return
        
        item_codes = [item['item_code'] for item in items]
        bin_map = self.fetch_bin_data(item_codes)
        range_data = {}

        for i in self.get_range_indices():
            from_date = self.filters.get(f"from_date_{i}")
            to_date = self.filters.get(f"to_date_{i}")

            if from_date and to_date:
                dn_map = self.fetch_qty_map(item_codes, "tabDelivery Note", "tabDelivery Note Item", "item_code", "posting_date", from_date, to_date)
                pr_map = self.fetch_qty_map(item_codes, "tabPurchase Receipt", "tabPurchase Receipt Item", "item_code", "posting_date", from_date, to_date)
                so_map = self.fetch_qty_map(item_codes, "tabSales Order", "tabSales Order Item", "custom_box", "transaction_date", from_date, to_date)
                range_data[i] = {"dn": dn_map, "pr": pr_map, "so": so_map}

        for item in items:
            row = {
                "item_code": item['item_code'],
                "item_name": item['item_name'],
                "stock_qty": bin_map.get(item['item_code'], 0),
            }

            for i in self.get_range_indices():
                row[f"dn_qty_{i}"] = range_data.get(i, {}).get("dn", {}).get(item['item_code'], 0)
                row[f"pr_qty_{i}"] = range_data.get(i, {}).get("pr", {}).get(item['item_code'], 0)
                row[f"so_qty_{i}"] = range_data.get(i, {}).get("so", {}).get(item['item_code'], 0)

            self.data.append(row)

    def run(self):
        self.build_data()
        return self.columns, self.data


def execute(filters=None):
    return StockMovementReport(filters).run()
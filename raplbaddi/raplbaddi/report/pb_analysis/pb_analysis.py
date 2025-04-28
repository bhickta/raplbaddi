import frappe

class StockMovementReport:
    def __init__(self, filters=None):
        self.filters = filters or {}
        self.columns = self.get_columns()
        self.data = []

    def get_columns(self):
        return [
            {"label": "Item Code", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 120},
            {"label": "Item Name", "fieldname": "item_name", "fieldtype": "Data", "width": 150},
            {"label": "Warehouse", "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 120},
            {"label": "Stock Qty", "fieldname": "stock_qty", "fieldtype": "Float", "width": 100},
            {"label": "DN Qty (Sales Range)", "fieldname": "dn_qty", "fieldtype": "Float", "width": 150},
            {"label": "PR Qty (Purchase Range)", "fieldname": "pr_qty", "fieldtype": "Float", "width": 150},
            {"label": "SO Qty (via DN)", "fieldname": "so_qty", "fieldtype": "Float", "width": 150},
        ]

    def fetch_items(self):
        conditions = []
        params = {}

        if self.filters.get("item_group"):
            conditions.append("i.item_group = %(item_group)s")
            params["item_group"] = self.filters.get("item_group")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        return frappe.db.sql(f"""
            SELECT
                i.item_code,
                i.item_name
            FROM `tabItem` i
            {where_clause}
        """, params, as_dict=1)

    def fetch_bin_data(self, item_codes):
        if not item_codes:
            return []

        return frappe.db.sql("""
            SELECT
                bin.item_code,
                bin.warehouse,
                bin.actual_qty
            FROM `tabBin` bin
            WHERE bin.item_code IN %(item_codes)s
        """, {"item_codes": item_codes}, as_dict=1)

    def fetch_dn_quantities(self, item_codes):
        if not item_codes or not (self.filters.get("sales_from_date") and self.filters.get("sales_to_date")):
            return []

        return frappe.db.sql("""
            SELECT
                dni.item_code as item_code,
                dni.warehouse,
                SUM(dni.qty) AS dn_qty
            FROM `tabDelivery Note Item` dni
            JOIN `tabDelivery Note` dn ON dn.name = dni.parent
            WHERE
                dni.item_code IN %(item_codes)s
                AND dn.posting_date BETWEEN %(from_date)s AND %(to_date)s
                AND dn.docstatus = 1
            GROUP BY dni.item_code, dni.warehouse
        """, {
            "item_codes": item_codes,
            "from_date": self.filters["sales_from_date"],
            "to_date": self.filters["sales_to_date"],
        }, as_dict=1)

    def fetch_pr_quantities(self, item_codes):
        if not item_codes or not (self.filters.get("pr_from_date") and self.filters.get("pr_to_date")):
            return []

        return frappe.db.sql("""
            SELECT
                pri.item_code,
                SUM(pri.qty) AS pr_qty
            FROM `tabPurchase Receipt Item` pri
            JOIN `tabPurchase Receipt` pr ON pr.name = pri.parent
            WHERE
                pri.item_code IN %(item_codes)s
                AND pr.posting_date BETWEEN %(from_date)s AND %(to_date)s
                AND pr.docstatus = 1
            GROUP BY pri.item_code
        """, {
            "item_codes": item_codes,
            "from_date": self.filters["pr_from_date"],
            "to_date": self.filters["pr_to_date"],
        }, as_dict=1)

    def fetch_so_quantities(self, item_codes):
        if not item_codes or not (self.filters.get("sales_from_date") and self.filters.get("sales_to_date")):
            return []

        return frappe.db.sql("""
            SELECT
                soi.custom_box as item_code,
                dni.warehouse,
                SUM(soi.qty) AS so_qty
            FROM `tabDelivery Note Item` dni
            JOIN `tabDelivery Note` dn ON dn.name = dni.parent
            JOIN `tabSales Order Item` soi ON soi.name = dni.so_detail
            WHERE
                soi.custom_box IN %(item_codes)s
                AND dn.posting_date BETWEEN %(from_date)s AND %(to_date)s
                AND dn.docstatus = 1
            GROUP BY soi.custom_box, dni.warehouse
        """, {
            "item_codes": item_codes,
            "from_date": self.filters["sales_from_date"],
            "to_date": self.filters["sales_to_date"],
        }, as_dict=1)

    def build_data(self):
        items = self.fetch_items()
        if not items:
            return

        item_codes = [item.item_code for item in items]

        bin_data = self.fetch_bin_data(item_codes)
        dn_data = self.fetch_dn_quantities(item_codes)
        pr_data = self.fetch_pr_quantities(item_codes)
        so_data = self.fetch_so_quantities(item_codes)

        # Create quick lookup dictionaries
        bin_map = {}
        for row in bin_data:
            bin_map.setdefault(row.item_code, []).append({
                "warehouse": row.warehouse,
                "stock_qty": row.actual_qty
            })

        dn_map = {(row.item_code, row.warehouse): row.dn_qty for row in dn_data}
        pr_map = {row.item_code: row.pr_qty for row in pr_data}
        so_map = {(row.item_code, row.warehouse): row.so_qty for row in so_data}

        # Build final rows
        for item in items:
            bins = bin_map.get(item.item_code, [{"warehouse": "", "stock_qty": 0}])

            for bin_info in bins:
                self.data.append({
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "warehouse": bin_info["warehouse"],
                    "stock_qty": bin_info["stock_qty"],
                    "dn_qty": dn_map.get((item.item_code, bin_info["warehouse"]), 0),
                    "pr_qty": pr_map.get(item.item_code, 0),
                    "so_qty": so_map.get((item.item_code, bin_info["warehouse"]), 0),
                })

    def run(self):
        self.build_data()
        return self.columns, self.data

def execute(filters=None):
    return StockMovementReport(filters).run()

import frappe


class StockMovementReport:
    def __init__(self, filters=None):
        self.filters = filters or {}
        self.columns = self.get_columns()
        self.data = []

    def get_columns(self):
        return [
            {
                "label": "Item Code",
                "fieldname": "item_code",
                "fieldtype": "Link",
                "options": "Item",
                "width": 120,
            },
            {
                "label": "Item Name",
                "fieldname": "item_name",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": "Stock Qty",
                "fieldname": "stock_qty",
                "fieldtype": "Float",
                "width": 100,
            },
            {
                "label": "DN Qty (Sales Range)",
                "fieldname": "dn_qty",
                "fieldtype": "Float",
                "width": 150,
            },
            {
                "label": "PR Qty (Purchase Range)",
                "fieldname": "pr_qty",
                "fieldtype": "Float",
                "width": 150,
            },
            {
                "label": "SO Qty (via DN)",
                "fieldname": "so_qty",
                "fieldtype": "Float",
                "width": 150,
            },
        ]

    def fetch_items(self):
        conditions = []
        params = {}

        if self.filters.get("item_group"):
            conditions.append("i.item_group = %(item_group)s")
            params["item_group"] = self.filters.get("item_group")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        return frappe.db.sql(
            f"""
            SELECT
                i.name AS item_code,
                i.item_name
            FROM `tabItem` i
            {where_clause}
        """,
            params,
            as_dict=1,
        )

    def fetch_bin_data(self, item_codes):
        if not item_codes:
            return []

        bin_data = frappe.db.sql(
            """
            SELECT
                bin.item_code,
                Sum(bin.actual_qty) AS actual_qty
            FROM `tabBin` bin
            WHERE bin.item_code IN %(item_codes)s
            GROUP BY bin.item_code
        """,
            {"item_codes": item_codes},
            as_dict=1,
        )
        return bin_data

    def fetch_dn_quantities(self, item_codes):
        if not item_codes or not (
            self.filters.get("from_date") and self.filters.get("to_date")
        ):
            return []

        return frappe.db.sql(
            """
            SELECT
                dni.item_code as item_code,
                SUM(dni.qty) AS dn_qty
            FROM `tabDelivery Note Item` dni
            JOIN `tabDelivery Note` dn ON dn.name = dni.parent
            WHERE
                dni.item_code IN %(item_codes)s
                AND dn.posting_date BETWEEN %(from_date)s AND %(to_date)s
                AND dn.docstatus = 1
            GROUP BY dni.item_code
        """,
            {
                "item_codes": item_codes,
                "from_date": self.filters["from_date"],
                "to_date": self.filters["to_date"],
            },
            as_dict=1,
        )

    def fetch_pr_quantities(self, item_codes):
        if not item_codes or not (
            self.filters.get("from_date") and self.filters.get("to_date")
        ):
            return []

        return frappe.db.sql(
            """
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
        """,
            {
                "item_codes": item_codes,
                "from_date": self.filters["from_date"],
                "to_date": self.filters["to_date"],
            },
            as_dict=1,
        )

    def fetch_so_quantities(self, item_codes):
        if not item_codes or not (
            self.filters.get("from_date") and self.filters.get("to_date")
        ):
            return []

        so_data = frappe.db.sql(
            """
            SELECT
            soi.custom_box AS item_code,
            SUM(soi.qty) AS so_qty
            FROM `tabSales Order Item` soi
            JOIN `tabSales Order` so ON so.name = soi.parent
            WHERE
            soi.custom_box IN %(item_codes)s
            AND so.transaction_date BETWEEN %(from_date)s AND %(to_date)s
            AND so.docstatus = 1
            GROUP BY soi.custom_box
        """,
            {
                "item_codes": item_codes,
                "from_date": self.filters["from_date"],
                "to_date": self.filters["to_date"],
            },
            as_dict=1,
        )
        return so_data

    def build_data(self):
        items = self.fetch_items()
        if not items:
            return

        item_codes = [item.item_code for item in items]

        bin_data = self.fetch_bin_data(item_codes)
        dn_data = self.fetch_dn_quantities(item_codes)
        pr_data = self.fetch_pr_quantities(item_codes)
        so_data = self.fetch_so_quantities(item_codes)

        dn_map = {row.item_code: row.dn_qty for row in dn_data}
        pr_map = {row.item_code: row.pr_qty for row in pr_data}
        so_map = {row.item_code: row.so_qty for row in so_data}

        bin_map = {}
        for bin in bin_data:
            bin_map[bin.item_code] = bin.actual_qty
        
        # Build final rows
        for item in items:
            self.data.append(
                {
                    "item_code": item.item_code,
                    "item_name": item.item_name,
                    "stock_qty": bin_map.get(item.item_code, 0),
                    "dn_qty": dn_map.get(item.item_code, 0),
                    "pr_qty": pr_map.get(item.item_code, 0),
                    "so_qty": so_map.get(item.item_code, 0),
                }
            )

    def run(self):
        self.build_data()
        return self.columns, self.data


def execute(filters=None):
    return StockMovementReport(filters).run()

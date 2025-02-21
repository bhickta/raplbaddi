import frappe

def execute():
    StockReconciliationManager(["Cooler", "DLP-Price List"]).execute()

class StockReconciliationManager:
    def __init__(self, restricted_item_groups):
        self.restricted_item_groups = restricted_item_groups

    def execute(self):
        self.disallow_negative_stock_for_selected()
        disabled_items = self.get_disabled_items()
        self.enable_disabled_items(disabled_items)
        disabled_warehouses = self.get_disabled_warehouses()
        self.enable_disabled_warehouses(disabled_warehouses)
        self.create_material_receipt_for_negative_stocks()
        self.reconcile_stock()
        self.disable_items(disabled_items)
        self.disable_warehouses(disabled_warehouses)

    def get_disabled_items(self):
        return frappe.get_all(
            "Item",
            fields=["name"],
            filters={
                "item_group": ["in", self.restricted_item_groups],
                "disabled": 1,
            },
        )

    def enable_disabled_items(self, disabled_items):
        if disabled_items:
            query = f"""
                UPDATE `tabItem`
                SET disabled = 0
                WHERE name IN ({", ".join([f"'{d.name}'" for d in disabled_items])})
            """
            frappe.db.sql(query)

    def disable_items(self, disabled_items):
        if disabled_items:
            query = f"""
                UPDATE `tabItem`
                SET disabled = 1
                WHERE name IN ({", ".join([f"'{d.name}'" for d in disabled_items])})
            """
            frappe.db.sql(query)

    def get_disabled_warehouses(self):
        return frappe.get_all(
            "Warehouse",
            fields=["name"],
            filters={"disabled": 1},
        )

    def enable_disabled_warehouses(self, disabled_warehouses):
        if disabled_warehouses:
            query = f"""
                UPDATE `tabWarehouse`
                SET disabled = 0
                WHERE name IN ({", ".join([f"'{w.name}'" for w in disabled_warehouses])})
            """
            frappe.db.sql(query)

    def disable_warehouses(self, disabled_warehouses):
        if disabled_warehouses:
            query = f"""
                UPDATE `tabWarehouse`
                SET disabled = 1
                WHERE name IN ({", ".join([f"'{w.name}'" for w in disabled_warehouses])})
            """
            frappe.db.sql(query)

    def disallow_negative_stock_for_selected(self):
        query = f"""
            UPDATE `tabItem`
            SET allow_negative_stock = 0 
            WHERE item_group IN ({', '.join([f"'{group}'" for group in self.restricted_item_groups])})
        """
        frappe.db.sql(query)

    def create_material_receipt_for_negative_stocks(self):
        negative_stocks = self.get_negative_stocks()
        if not negative_stocks:
            return

        mr = frappe.new_doc("Stock Entry")
        mr.stock_entry_type = "Material Receipt"
        mr.posting_date = frappe.utils.nowdate()
        mr.posting_time = frappe.utils.nowtime()
        mr.company = "Real Appliances Private Limited"

        for item, warehouse, qty in negative_stocks:
            mr.append(
                "items",
                {
                    "item_code": item,
                    "t_warehouse": warehouse,
                    "qty": abs(qty),
                    "basic_rate": 0,
                },
            )
        
        mr.insert()
        mr.submit()
        self.mr = mr

    def get_negative_stocks(self):
        query = f"""
            SELECT
                bn.item_code, bn.warehouse, bn.actual_qty
            FROM
                `tabBin` bn
            LEFT JOIN
                `tabItem` it on bn.item_code = it.name
            WHERE
                bn.actual_qty < 0
                AND it.item_group IN ({', '.join([f"'{group}'" for group in self.restricted_item_groups])})
        """
        return frappe.db.sql(query)

    def reconcile_stock(self):
        stock_items = self.get_item_warehouse_from_bin_entry()
        if not stock_items:
            return
        
        sr = frappe.new_doc("Stock Reconciliation")
        sr.purpose = "Stock Reconciliation"
        sr.posting_date = frappe.utils.nowdate()
        sr.posting_time = frappe.utils.nowtime()
        sr.set_posting_time = 1
        sr.company = "Real Appliances Private Limited"
        
        sr.expense_account = (
            frappe.get_cached_value("Company", sr.company, "stock_adjustment_account")
            or frappe.get_cached_value("Account", {"account_type": "Stock Adjustment", "company": sr.company}, "name")
            if frappe.get_all("Stock Ledger Entry", {"company": sr.company})
            else frappe.get_cached_value("Account", {"account_type": "Temporary", "company": sr.company}, "name")
        )
        
        sr.cost_center = (
            frappe.get_cached_value("Company", sr.company, "cost_center")
            or frappe.get_cached_value("Cost Center", filters={"is_group": 0, "company": sr.company})
        )
        
        for item, warehouse in stock_items:
            sr.append(
                "items",
                {
                    "item_code": item,
                    "warehouse": warehouse,
                    "qty": 0,
                    "valuation_rate": 0,
                    "reconcile_all_serial_batch": 1,
                },
            )
        
        sr.insert()
        sr.submit()

    def get_item_warehouse_from_bin_entry(self):
        query = f"""
            SELECT
                bn.item_code, bn.warehouse
            FROM
                `tabBin` bn
            LEFT JOIN
                `tabItem` it on bn.item_code = it.name
            WHERE
                it.item_group IN ({', '.join([f"'{group}'" for group in self.restricted_item_groups])})
                AND bn.actual_qty > 0
        """
        return frappe.db.sql(query)

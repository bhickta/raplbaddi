import frappe
import os
import openpyxl
from erpnext import get_default_company
from io import BytesIO

def execute(file_name_or_id="/files/zero_stock_nov_2025_01.xlsx"):
    manager = StockReconciliationManager(file_name_or_id)
    manager.execute_custom_reconciliation()

class StockReconciliationManager:
    def __init__(self, items_file=None):
        self.items_file = items_file

    def execute_custom_reconciliation(self):
        disabled_stock_items = self.get_disabled_items_for_reconciliation()
        file_stock_items = self.get_items_from_file_for_reconciliation()

        all_items_to_reconcile = set(disabled_stock_items) | set(file_stock_items)
        
        if not all_items_to_reconcile:
            frappe.msgprint("No items found to reconcile.")
            return

        originally_disabled_item_codes = {item for item, wh in disabled_stock_items}

        if originally_disabled_item_codes:
            self.enable_items(originally_disabled_item_codes)

        try:
            self.reconcile_stock(list(all_items_to_reconcile))
            frappe.msgprint(f"Successfully reconciled {len(all_items_to_reconcile)} item/warehouse entries.")
        finally:
            if originally_disabled_item_codes:
                self.disable_items(originally_disabled_item_codes)
                frappe.msgprint("Re-disabled original items.")

    def enable_items(self, item_codes):
        if item_codes:
            query = """
                UPDATE `tabItem`
                SET disabled = 0
                WHERE name IN %s
            """
            frappe.db.sql(query, (list(item_codes),))
            frappe.msgprint(f"Temporarily enabled {len(item_codes)} disabled items.")

    def disable_items(self, item_codes):
        if item_codes:
            query = """
                UPDATE `tabItem`
                SET disabled = 1
                WHERE name IN %s
            """
            frappe.db.sql(query, (list(item_codes),))
            frappe.msgprint(f"Disabled {len(item_codes)} items back to original state.")

    def get_disabled_items_for_reconciliation(self):
        query = """
            SELECT
                bn.item_code, bn.warehouse
            FROM
                `tabBin` bn
            LEFT JOIN
                `tabItem` it on bn.item_code = it.name
            WHERE
                it.disabled = 1
                AND bn.actual_qty != 0
        """
        result = frappe.db.sql(query, as_list=True)
        return [tuple(row) for row in result]

    def get_items_from_file_for_reconciliation(self):
        if not self.items_file:
            frappe.throw("No Excel file specified for item reconciliation.")

        item_codes = self.read_item_codes_from_file()

        if not item_codes:
            return []

        query = """
            SELECT
                bn.item_code, bn.warehouse
            FROM
                `tabBin` bn
            WHERE
                bn.item_code IN %s
                AND bn.actual_qty != 0
        """
        result = frappe.db.sql(query, (item_codes,), as_list=True)
        return [tuple(row) for row in result]

    def read_item_codes_from_file(self):
        file_doc = frappe.get_doc("File", {"file_url": self.items_file})
        if not file_doc:
            frappe.throw(f"File not found: {self.items_file}")

        item_codes = []

        try:
            file_content = file_doc.get_content()
            
            workbook = openpyxl.load_workbook(BytesIO(file_content), read_only=True, data_only=True)
            sheet = workbook.active

            is_header = True
            for row in sheet.iter_rows():
                if is_header:
                    is_header = False
                    continue
                
                if not row or len(row) < 2:
                    continue

                item_code_cell = row[1]
                item_code = item_code_cell.value

                if item_code:
                    item_codes.append(str(item_code).strip())

        except Exception as e:
            frappe.throw(f"Error reading Excel file {self.items_file}: {e}")

        return list(set(item_codes))

    def reconcile_stock(self, stock_items):
        if not stock_items:
            return
        
        BATCH_SIZE = 500
        
        for i in range(0, len(stock_items), BATCH_SIZE):
            batch = stock_items[i:i + BATCH_SIZE]
            
            sr = frappe.new_doc("Stock Reconciliation")
            sr.purpose = "Stock Reconciliation"
            sr.posting_date = frappe.utils.nowdate()
            sr.posting_time = frappe.utils.nowtime()
            sr.set_posting_time = 1
            sr.company = get_default_company()

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

            for item, warehouse in batch:
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
            frappe.msgprint(f"Stock Reconciliation {sr.name} (Batch {i//BATCH_SIZE + 1}) created and submitted.")
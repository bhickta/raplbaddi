import erpnext.exceptions
import frappe
from datetime import datetime
import csv
import erpnext
import frappe.utils

class StockReconciliationManager:
    def __init__(self, file_name):
        self.csv_file_path = self.get_csv_file_path(file_name)
        self.initially_disabled_items = set()

    def get_csv_file_path(self, file_name):
        return frappe.get_site_path("private", "files", file_name)

    def process_reconciliations(self):
        with open(self.csv_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)
            data = [frappe._dict(zip(headers, row)) for row in reader]
            
            self.store_initially_disabled_items()
            self.toggle_items_enabled_status(enable=True)
            
            for row in data:
                self.cancel_and_create_reconciliation(row.stock_reconcilliation, self.convert_date(row.new_date))
            
            self.toggle_items_enabled_status(enable=False)

    def cancel_and_create_reconciliation(self, stock_reconciliation_id, new_date):
        try:
            stock_reconciliation = frappe.get_doc("Stock Reconciliation", stock_reconciliation_id)
            if stock_reconciliation.docstatus != 2:
                stock_reconciliation.cancel()
                print(f"Cancelled Stock Reconciliation {stock_reconciliation_id}.")
                
            item_data = stock_reconciliation.items
            sc_items = [item for item in item_data if item.warehouse.startswith("SC-")]
            other_items = [item for item in item_data if not item.warehouse.startswith("SC-")]

            if sc_items:
                self.create_amended_reconciliation(stock_reconciliation, sc_items, new_date)
            if other_items:
                self.create_new_reconciliation(stock_reconciliation, other_items, stock_reconciliation.posting_date)
        except Exception as e:
            raise e

    def create_amended_reconciliation(self, stock_reconciliation, items, posting_date):
        changed_fields = {"posting_date": posting_date, "set_posting_time": True}
        rows_updated = {"items": items}
        amended_stock_reconciliation = self.amend_document(stock_reconciliation, changed_fields, rows_updated, submit=True)
        main_warehouse = items[0].warehouse
        sc_details = self.set_service_centre_details({"main_warehouse": main_warehouse})
        self.change_warehouse_in_dnpr(sc_details, main_warehouse, posting_date)
        print(f"Successfully created amended Stock Reconciliation {amended_stock_reconciliation.name} with date {posting_date}")

    def create_new_reconciliation(self, stock_reconciliation, items, posting_date):
        new_stock_reconciliation = frappe.copy_doc(stock_reconciliation)
        new_stock_reconciliation.docstatus = 0
        new_stock_reconciliation.posting_date = posting_date
        new_stock_reconciliation.set_posting_time = True
        new_stock_reconciliation.items = items
        new_stock_reconciliation.save()
        
        if not new_stock_reconciliation.items:
            print("No items to reconcile in new document")
        else:
            new_stock_reconciliation.submit()
            print(f"Successfully created new Stock Reconciliation {new_stock_reconciliation.name} with date {posting_date}")

    def store_initially_disabled_items(self):
        self.initially_disabled_items = set(
            frappe.db.sql_list("SELECT name FROM `tabItem` WHERE disabled = 1")
        )

    def toggle_items_enabled_status(self, enable):
        if enable:
            frappe.db.sql("""UPDATE `tabItem` SET disabled = 0 WHERE disabled = 1""")
            print("Enabled all previously disabled items in the Items table")
        else:
            if self.initially_disabled_items:
                frappe.db.sql(
                    """UPDATE `tabItem` SET disabled = 1 WHERE name IN ({})""".format(
                        ", ".join(f"'{item}'" for item in self.initially_disabled_items)
                    )
                )
                print("Restored initial disabled items.")

    def convert_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return date_str

    def amend_document(self, amend_from, changed_fields, rows_updated, submit=False):
        amended_doc = frappe.copy_doc(amend_from)
        amended_doc.amended_from = amend_from.name
        amended_doc.update(changed_fields)
        for child_table in rows_updated:
            amended_doc.set(child_table, rows_updated[child_table])
        if submit:
            frappe.flags.ignore_party_validation = True
            try:
                amended_doc.submit()
            except FileNotFoundError as e:
                amended_doc.submit()
        return amended_doc

    def set_service_centre_details(self, filters=None):
        return frappe.get_all("Service Centre", fields=["name", "main_warehouse", "customer", "supplier"], filters=filters)[0]

    def process_documents(self, doctype, party_field, party_name, new_warehouse, error_log):
        doc_list = frappe.get_all(
            doctype,
            filters={
                party_field: party_name,
                "posting_date": ["between", [self.start_date, self.end_date]],
                "docstatus": 1,
            },
            pluck="name"
        )
        
        for doc_name in doc_list:
            doc = frappe.get_doc(doctype, doc_name)
            doc.cancel()
            
            for item in doc.items:
                item.warehouse = new_warehouse
            
            new_doc = self.amend_document(
                doc,
                changed_fields={"posting_date": doc.posting_date, "set_posting_time": True},
                rows_updated={"items": doc.items},
                submit=False,
            )
            
            try:
                new_doc.submit()
            except erpnext.exceptions.PartyDisabled:
                frappe.db.set_value(party_field.split("_")[0].capitalize(), party_name, "disabled", 0)
                new_doc.submit()
                frappe.db.set_value(party_field.split("_")[0].capitalize(), party_name, "disabled", 1)
            except FileNotFoundError as e:
                new_doc.submit()
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), error_log)
                raise e
            
            print(f"Successfully processed {new_doc}")

    def change_warehouse_in_dnpr(self, sc, new_warehouse, posting_date):
        self.start_date = posting_date
        self.end_date = frappe.utils.today()
        
        self.process_documents("Delivery Note", "customer", sc.customer, new_warehouse, "DN Submit Error")
        self.process_documents("Purchase Receipt", "supplier", sc.supplier, new_warehouse, "PR Submit Error")

    @staticmethod
    def execute(file_name):
        manager = StockReconciliationManager(file_name)
        manager.process_reconciliations()
    
def execute():
    StockReconciliationManager.execute("stock_reconcilliation_sc.csv")
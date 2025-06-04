import frappe
import frappe.utils
from frappe.utils import csvutils, re
from collections import defaultdict

class Unit2DataImporter:

    def execute(self, delete=False):
        frappe.flags.in_patch = True
        self.set_data()
        self.process_data(delete=delete)

    def set_data(self):
        file_path = frappe.utils.get_files_path("unit_2_sales_data.csv")
        with open(file_path, "rb") as file:
            self.data = csvutils.read_csv_content(file.read())
    
    def enable_disabled_items(self):
        self.disabled_items = frappe.get_all(
            "Item",
            filters={"disabled": 1},
            fields=["name"],
        )
        # enable all disabled items
        frappe.db.sql(
            """
            UPDATE `tabItem`
            SET disabled = 0
            WHERE name IN %(names)s
            """,
            {"names": [item.name for item in self.disabled_items]},            
        )
    
    def redisable_items(self):
        # disable all items that were previously disabled
        frappe.db.sql(
            """
            UPDATE `tabItem`
            SET disabled = 1
            WHERE name IN %(names)s
            """,
            {"names": [item.name for item in self.disabled_items]},
        )

    def process_data(self, delete=False):
        if delete:
            self.cancel_and_delete_delivery_notes()
            return
        self.enable_disabled_items()
        self.create_dict()
        self.clean_data()
        self.group_data()
        self.create_delivery_note()
        self.redisable_items()

    def create_dict(self):
        self.data_dict = []
        for row in self.data[1:]:
            item_code, item_name = re.split(r"\s+", row[3], 1)
            entry = {
                "customer": row[0],
                "customer_name": row[1],
                "sales_person": row[2],
                "item_code": item_code.strip("()"),
                "item_name": item_name,
                "qty": int(row[4]),
            }
            for key in entry:
                if isinstance(entry[key], str):
                    entry[key] = entry[key].strip()
            self.data_dict.append(entry)
    
    def clean_data(self):
        sales_person_map = {
            "Mir Farooq": "E-C-14 Farooq Kashmir",
            "Navdeep Singla": "E-C-15 Navdeep Singla",
            "Prince Bansal Mansa": "E-C-17 Prince Bansal",
            "Puspendra":  "E-C-3 Puspendra Kumar",
            "Prince Kumar": "E-C-19 Prince Verma",
            "Sahil Sood": "E-B-27 Sahil Sood",
            "Vikas Sharma": "E-C-16 Vikas Sharma",
        }
        custoemer_map = {
            "P-MNS-003": "P-MNS-UT-1",
        }
        item_code_map = {
            "5": "G5A",
            "G25SPC": "LG25SPC",
        }
        
        for row in self.data_dict:
            name = row.get("sales_person")
            if name in sales_person_map:
                row["sales_person"] = sales_person_map[name]
            name = row.get("customer")
            if name in custoemer_map:
                row["customer"] = custoemer_map[name]
            name = row.get("item_code")
            if name in item_code_map:
                row["item_code"] = item_code_map[name]

    def group_data(self):
        # Group by (customer, customer_name, sales_person, item_code, item_name)
        self.grouped_data = defaultdict(lambda: {"qty": 0})
        
        for row in self.data_dict:
            key = (
                row["customer"],
                row["customer_name"],
                row["sales_person"],
                row["item_code"],
                row["item_name"],
            )
            self.grouped_data[key]["qty"] += row["qty"]

    def create_delivery_note(self):
        # Group keys by (customer, customer_name, sales_person)
        dn_groups = defaultdict(list)

        for key, data in self.grouped_data.items():
            customer, customer_name, sales_person, item_code, item_name = key
            dn_key = (customer, customer_name, sales_person)
            dn_groups[dn_key].append({
                "item_code": item_code,
                "item_name": item_name,
                "qty": data["qty"]
            })

        # Create one DN per customer-sales_person group
        print(len(dn_groups), "Delivery Notes to be created")
        for (customer, customer_name, sales_person), items in dn_groups.items():
            doc = frappe.new_doc("Delivery Note")
            doc.customer = customer
            doc.customer_name = customer_name
            doc.naming_series = "DNU2-.####."
            doc.sales_person = sales_person

            for item in items:
                doc.append(
                    "items",
                    {
                        "item_code": item["item_code"],
                        "item_name": item["item_name"],
                        "qty": item["qty"],
                        "rate": 0.0,
                    },
                )

            doc.update(
                {
                    "custom_vehicle_no": "Other",
                    "transporter": "Other",
                    "driver_number": "0000000000",
                    "bilty_no": "000000",
                }
            )
            doc.append(
                "freight",
                {
                    "type": "Basic",
                    "amount": 0.0,
                },
            )
            doc.save()
            doc.submit()
            print(doc)

    def cancel_and_delete_delivery_notes(self):
            delivery_notes = frappe.get_all(
                "Delivery Note",
                filters={"naming_series": "DNU2-.####."},
                fields=["name"]
            )
            from erpnext.stock.doctype.repost_item_valuation.repost_item_valuation import repost_entries
            repost_entries()
            for dn_name in delivery_notes:
                repost_entry = frappe.get_all("Repost Item Valuation", {"voucher_type": "Delivery Note", "voucher_no": dn_name.name})
                print(f"Repost Entry: {repost_entry}")
                if repost_entry:
                    repost_doc = frappe.get_doc("Repost Item Valuation", repost_entry[0].name)
                    print(f"Reposting Item Valuation for Delivery Note: {dn_name.name}")
                    repost_doc.cancel()
                    repost_doc.delete(delete_permanently=True)
                try:
                    print(f"Processing Delivery Note: {dn_name.name}")
                    doc = frappe.get_doc("Delivery Note", dn_name.name)
                    if doc.docstatus == 1: # Check if submitted
                        doc.cancel()
                        print(f"Cancelled Delivery Note: {doc.name}")
                    if doc.docstatus == 0: # Now it should be draft or already draft
                        print(f"Deleted Delivery Note: {doc.name}")
                    doc.delete(delete_permanently=True)
                except Exception as e:
                    frappe.log_error(f"Error processing Delivery Note {dn_name.name}: {e}")
                    raise e

def execute(delete=False):
    importer = Unit2DataImporter()
    importer.execute(delete=delete)
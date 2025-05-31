import frappe
import frappe.utils
from frappe.utils import csvutils, re
from collections import defaultdict

class Unit2DataImporter:

    def execute(self):
        frappe.flags.in_patch = True
        self.set_data()
        self.process_data()

    def set_data(self):
        file_path = frappe.utils.get_files_path("unit_2_sales_data.csv")
        with open(file_path, "rb") as file:
            self.data = csvutils.read_csv_content(file.read())

    def process_data(self):
        self.create_dict()
        self.clean_data()
        self.group_data()
        self.create_delivery_note()
        frappe.db.commit()

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


def execute():
    importer = Unit2DataImporter()
    importer.execute()
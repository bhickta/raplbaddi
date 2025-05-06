import frappe
from frappe.model.document import Document
from erpnext import get_default_company

class PBCreationTool(Document):
    def get_item_code(self, item, item_type):
        item_code_formats = {
            "Box": f'PB{item.capacity}{item.model[:1]} {self.box_particular}',
            "Paper": f'PP {self.box_particular} {item.paper_name}',
        }
        return item_code_formats.get(item_type)
    
    def paper_safety_stock(self, i):
        safety_stock_list = [item.safety_stock for item in self.items if i.paper_name == item.paper_name]
        return sum(safety_stock_list)   
  
    def before_submit(self):
        self.on_update_after_submit()

    def on_update_after_submit(self):
        for item in self.items:
            box_code, paper_code = item.box or self.get_item_code(item, item_type="Box"), item.paper or self.get_item_code(item, item_type="Paper")
            enable_paper = False if len([item.box_enabled for item in self.items if item.box_enabled]) == 0 else True
            box, paper = self.get_or_create_item(box_code, paper_code, item, self.paper_safety_stock(item))
            if not item.box_enabled:
                box.disabled = True
            paper.disabled = not enable_paper
            box.save(), paper.save()
            print(box.brand, box.geyser_model)

    def get_or_create_item(self, box_code, paper_code, item, total_safety_stock):
        try:
            box = frappe.get_doc("Item", box_code)
        except frappe.exceptions.DoesNotExistError:
            box = self.create_item(box_code, item)

        try:
            paper = frappe.get_doc("Item", paper_code)
        except frappe.exceptions.DoesNotExistError:
            paper = self.create_item(paper_code, item)

        self.set_item_details(box, box_code, item)
        self.set_item_details(paper, paper_code, item)
        item.box = box.name
        item.paper = paper.name
        box.disabled = not item.box_enabled
        box.safety_stock = item.safety_stock if box.safety_stock == 0 and self.docstatus == 0 else box.safety_stock
        box.custom_paper_name, paper.custom_paper_name = item.paper_name, item.paper_name
        return box, paper

    def set_item_details(self, item, box_code, i):
        item.item_code = box_code
        item.item_name = box_code
        item.name = box_code
        item.description = box_code
        item.item_group = 'Packing Boxes' if box_code.startswith('PB') else 'Packing Paper'
        item.geyser_model = i.model
        item.capacity = i.capacity,
        item.safety_stock = i.safety_stock if item.item_group == 'Packing Boxes' else i.safety_stock * (i.paper_name.count('-') + 1)
        item.paper_name = i.paper_name
        item.stock_uom = 'Nos' if item.item_group == 'Packing Boxes' else 'Set 2'
        item.is_stock_item = 1

        if self.box_type == 'Brand':
            item.brand = self.box_particular
        else:
            item.plain_box_type = self.box_particular

        if not item.item_defaults:
            item.append("item_defaults", {"default_warehouse": 'Packing Boxes - Rapl', "company": get_default_company()})

    def create_item(self, box_code, i):
        item = frappe.new_doc("Item")
        self.set_item_details(item, box_code, i)
        item.save()
        return item

    def on_cancel(self):
        for item in self.items:
            self.disable_item(item.box)
            self.disable_item(item.paper)
 
    def disable_item(self, item_code):
        box = frappe.get_doc("Item", item_code)
        box.disabled = 1
        box.save()
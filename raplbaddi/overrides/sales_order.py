import frappe
import frappe.utils

def validate(doc, method):
    validate_bill_to_ship_to(doc)
    validate_mandatory_fields(doc)
    
def validate_mandatory_fields(doc):
    if not doc.is_new():
        return
    mandatory_fields = ["taxes_and_charges"]
    for field in mandatory_fields:
        field_meta = frappe.get_meta(doc.doctype).get_field(field)
        label = field_meta.label if field_meta else field
        if not doc.get(field):
            frappe.throw(f"{label} is mandatory")

def validate_bill_to_ship_to(doc):
    bill_to_ship_to = doc.is_bill_to_ship_to
    billing_gstin = frappe.get_value("Address", doc.customer_address, "gstin")
    shipping_gstin = frappe.get_value("Address", doc.shipping_address_name, "gstin")
    if billing_gstin != shipping_gstin and not bill_to_ship_to:
        frappe.throw(("Please Check Bill To and Ship To if Billing and Shipping GSTIN are not same"))

@frappe.whitelist()
def update_custom_box_backend(item_code, name_of_brand, cdt, cdn):
    geyser_details = frappe.db.get_value('Item', item_code, 'geyser_box_size', as_dict=True)
    if not geyser_details or not geyser_details.get('geyser_box_size'):
        return {'custom_box': ''}

    box_size_details = frappe.db.get_value('Geyser Box Size', geyser_details['geyser_box_size'], ['capacity', 'model'], as_dict=True)
    if not box_size_details:
        return {'custom_box': ''}

    packing_boxes = frappe.db.get_list(
        'Item',
        fields=['name'],
        filters={
            'item_group': 'Packing Boxes',
            'capacity': box_size_details['capacity'],
            'geyser_model': box_size_details['model'],
            'brand': name_of_brand,
            'disabled': 0,
        }
    )
    if len(packing_boxes) > 1:
        error = [f"Multiple packing boxes found for {item_code} with capacity {box_size_details['capacity']} and model {box_size_details['model']}. Please check the packing box item group."]
        error.append(f"Packing Boxes: {', '.join([frappe.utils.get_link_to_form('Item', box['name']) for box in packing_boxes])}")
        frappe.throw("<br>".join(error))

    if not packing_boxes:
        error = [f"No packing box found for {item_code} with capacity {box_size_details['capacity']} and model {box_size_details['model']}. Please check the packing box item group."]
        # frappe.msgprint("<br>".join(error))
        return {'custom_box': ''}

    custom_box = packing_boxes[0]['name']
    return {'custom_box': custom_box}
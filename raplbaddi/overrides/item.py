import frappe
from erpnext.stock.doctype.item.item import get_uom_conv_factor

def validate(doc, method):
    validate_uom_conversion_factor(doc)
    validate_cbm(doc)

def validate_cbm(doc):
    if doc.cbm_height and doc.cbm_width and doc.cbm_length:
        doc.cbm = (doc.cbm_height * doc.cbm_width * doc.cbm_length)/1000000000

def validate_uom_conversion_factor(doc):
    def validate_gram_kgs_conversion_multiple(doc):
        uoms_list = {}    
        for d in doc.get("uoms"):
            if not d.conversion_multiple:
                continue
            uoms_list[d.uom] = d.conversion_multiple
        if "KGS" in uoms_list and "Gram" not in uoms_list:
            doc.append("uoms", {"uom": "Gram", "conversion_multiple": get_uom_conv_factor("Gram", "KGS")})
        elif "Gram" in uoms_list and "KGS" not in uoms_list:
            doc.append("uoms", {"uom": "KGS", "conversion_multiple": get_uom_conv_factor("KGS", "Gram")})
    # validate_gram_kgs_conversion_multiple(doc)

    if doc.uoms:
        for d in doc.uoms:
            if not d.conversion_multiple:
                d.conversion_multiple = 1
            d.conversion_factor = 1/d.conversion_multiple
            d.base_uom = doc.stock_uom
        

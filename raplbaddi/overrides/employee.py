import frappe


def autoname(doc, method):
    doc.employee, doc.name = None, None

    if not doc.department or doc.branch == None:
        frappe.throw("Department and branch is Mandatory")

    if len(frappe.get_all("Employee")) == 0:
        middle_no = 1
    else:
        last_employee = frappe.get_last_doc("Employee").name.split("-")

        middle_no = get_middle_no(last_employee[1])
        if int(last_employee[2]) == 30:
            middle_no += + 1

    doc.naming_series = f"E-{get_middle_no(middle_no)}-.#"

def get_middle_no(value):
    if isinstance(value, int):
        if value < 1:
            raise ValueError("Input must be a positive integer.")
        
        result = ""
        
        while value > 0:
            value -= 1
            result = chr(value % 26 + ord('A')) + result
            value //= 26
        
        return result
    
    elif isinstance(value, str):
        result = 0
        for char in value:
            result = result * 26 + (ord(char) - ord('A') + 1)
        return result
    else:
        raise ValueError("Input must be an integer or a string.")
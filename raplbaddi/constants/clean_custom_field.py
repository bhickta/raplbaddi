import os

custom_fields = [
]

def main():
    field_required = ["name", "label", "fieldname", "fieldtype", "options", "default", "insert_after", "reqd", "allow_on_submit"]
    dump = [{k: v for k, v in entry.items() if k in field_required} for entry in custom_fields]
    
    file_path = os.path.join(os.path.dirname(__file__), 'dump.py')
    
    with open(file_path, 'w') as file:
        file.write(f"custom_fields = {dump}")
    
    print(f"Data has been written to {file_path}")

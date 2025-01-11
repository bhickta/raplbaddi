import frappe
from frappe.core.doctype.user_permission.user_permission import get_user_permissions

class ServiceCentreReport:
    def __init__(self, filters=None):
        self.filters = filters or {}
        self.allowed_service_centres = []

    def get_allowed_service_centres(self):
        user_permissions = get_user_permissions(frappe.session.user)
        allowed_service_centres = [groups['doc'] for groups in user_permissions.get('Service Centre', [])]
        return allowed_service_centres

    def validate_permissions(self):
        self.allowed_service_centres = self.get_allowed_service_centres()
    
    def run(self):
        self.validate_permissions()
        data = self.fetch_data()
        columns = self.get_columns()
        return columns, data
    
    def get_columns(self):
        pass
    
    def fetch_data(self):
        pass
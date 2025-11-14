# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.core.doctype.user_permission.user_permission import get_user_permissions

class ReportFullAccessUsers(Document):
	pass

@frappe.whitelist()
def get_wildcard_users():
    users= frappe.get_all(
			"Report Full Access Users",
			fields=["user", "check"]
		)
    wildcard_users = [user['user'] for user in users]
    wildcard_users.append('Administrator')
    return wildcard_users
  
def permission_decorator(doc, value, user=frappe.session.user):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if user in get_wildcard_users():
                return func(*args, **kwargs)
            try:
                allowed_values = [item['doc'] for item in get_user_permissions(user=user)[doc]]
                if value in allowed_values:
                    return func(*args, **kwargs)
                else:
                  pass
            except:
                pass
        return wrapper

    return decorator
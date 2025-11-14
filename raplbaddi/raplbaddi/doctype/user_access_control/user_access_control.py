import frappe
from frappe.model.document import Document
from frappe.utils import now
from frappe.core.doctype.user_permission.user_permission import UserPermission


class UserAccessControl(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        frappe.flags.ignore_permission = True

    def validate(self):
        self.sort_by_doctype()
        self.sync_and_cleanup_permissions()
        self.validate_mandatory()

    def validate_mandatory(self):
        for item in self.items:
            if not (item.apply_to_all_doctypes or item.applicable_for) or (item.apply_to_all_doctypes and item.applicable_for):
                frappe.throw(
                    "Either apply access control for <b>All</b> or for <b>One</b>"
                )
            if not item.permission:
                frappe.throw("Permission is mandatory in items")

    def on_trash(self):
        self.delete_all_permissions_for_user(self.user)

    def sort_by_doctype(self):
        self.items.sort(key=lambda x: x.allow)

    def sync_and_cleanup_permissions(self):
        self.sync_permission()
        existing_permissions = self._get_user_permissions(self.user)
        self.cleanup_stale_permissions(existing_permissions)

    def sync_permission(self):
        for item in self.items:
            permission = self.get_or_create_user_permission(item)
            if not isinstance(permission, str):
                permission = permission.name
            item.permission = permission

    def get_or_create_user_permission(self, item) -> UserPermission:
        permission_dict = self._get_permission_dict(item, as_filter=True)
        doc = self.get_user_permission(permission_dict)
        if not doc:
            doc = self.insert_user_permission(permission_dict)
        return doc

    def cleanup_stale_permissions(self, existing_permissions):
        valid_permissions = {item.permission for item in self.items}
        for permission in existing_permissions:
            if permission not in valid_permissions:
                self.delete_permission(permission)

    def insert_user_permission(self, permission_dict):
        from frappe.core.doctype.user_permission.user_permission import UserPermission
        UserPermission.validate_user_permission = _validate_user_permission
        permission_dict.doctype = "User Permission"
        return frappe.get_doc(permission_dict).insert(ignore_permissions=True)

    def delete_permission(self, permission):
        frappe.db.delete("User Permission", {"name": permission})

    def delete_all_permissions_for_user(self, user):
        frappe.db.delete("User Permission", {"user": user})

    def get_user_permission(self, permission_dict):
        return frappe.get_value("User Permission", permission_dict) or None

    def _get_user_permissions(self, user):
        return frappe.get_all(
            "User Permission", filters={"user": user}, pluck="name"
        )

    def _get_permission_dict(self, item, as_filter=False):
        permission_dict = frappe._dict(
            {
                "allow": item.allow,
                "apply_to_all_doctypes": item.apply_to_all_doctypes,
                "applicable_for": item.applicable_for,
                "for_value": item.for_value,
                "user": self.user,
                "is_default": item.is_default,
            }
        )
        if not as_filter:
            permission_dict.update({"permission": item.permission})
        return permission_dict

    @frappe.whitelist()
    def get_user_permissions(self, user):
        permissions = self._get_user_permissions(user)
        return [frappe.get_doc("User Permission", name) for name in permissions]

def _validate_user_permission(self):
    return
import frappe

def execute():
    users = frappe.get_all("User Permission", pluck="user", distinct=True)
    
    for user in users:
        user_permissions = frappe.get_all("User Permission", filters={"user": user}, fields=["allow", "apply_to_all_doctypes", "applicable_for", "for_value", "is_default"])
        if user_permissions:
            create_user_access_control_for_existing_permissions(user, user_permissions)

def create_user_access_control_for_existing_permissions(user, user_permissions):
    if not frappe.db.exists("User Access Control", {"user": user}):

        user_access_control = frappe.new_doc("User Access Control")
        user_access_control.user = user
        user_access_control.user_name = frappe.get_value("User", user, "full_name")

        for permission in user_permissions:
            user_access_control.append("items", {
                "allow": permission.get("allow"),
                "apply_to_all_doctypes": permission.get("apply_to_all_doctypes", 0),
                "applicable_for": permission.get("applicable_for", ""),
                "for_value": permission.get("for_value", ""),
                "is_default": permission.get("is_default", 0),
                "permission": None  # This will be populated during sync
            })

        user_access_control.insert()
        frappe.db.commit()

        user_access_control.sync_and_cleanup_permissions()
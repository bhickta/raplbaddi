import json
import frappe

def execute():
    # Get the currently installed apps
    installed_apps = frappe.get_installed_apps()

    # Remove "raplbaddi" from the list
    if "raplbaddi" in installed_apps:
        installed_apps.remove("raplbaddi")

    # Append "raplbaddi" to the end of the list
    installed_apps.append("raplbaddi")

    # Update the global setting
    frappe.db.set_global("installed_apps", json.dumps(installed_apps))
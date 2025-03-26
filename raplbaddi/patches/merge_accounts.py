import frappe
from erpnext.accounts.doctype.account.account import merge_account

def execute():
    accounts_to_merge = frappe.get_all(
        "Account",
        filters=[["name", "not like", "%rapl%"]],
        fields=["name"],
        pluck="name"
    )
    for account in accounts_to_merge:
        print(account)
        new_account = account.split("-")[0] + "- RAPL"
        merge_account(account, new_account)
    frappe.db.commit()
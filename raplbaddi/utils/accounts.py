import frappe
from frappe.utils import nowdate

def create_journal_entry(
    source_doc,
    acc1=None,
    acc1_exc_rate=None,
    acc2_exc_rate=None,
    acc2=None,
    acc1_amount=0,
    acc2_amount=0,
    posting_date=None,
    cost_center=None,
    **kwargs
):
    if not acc1_amount and not acc2_amount:
        return
    je = frappe.new_doc("Journal Entry")
    je.posting_date = posting_date or nowdate()
    je.company = source_doc.company
    je.user_remark = source_doc.name
    je.multi_currency = True
    if not cost_center:
        cost_center = source_doc.cost_center
    print(acc1_amount, acc2_amount)
    je.set(
        "accounts",
        [
            {
                "account": acc1,
                "cost_center": cost_center,
                "debit_in_account_currency": acc1_amount,
                "custom_reference_type": source_doc.doctype,
                "custom_reference_name": source_doc.name,
            },
            {
                "account": acc2,
                "cost_center": cost_center,
                "party_type": kwargs.get("party_type"),
                "party": kwargs.get("party"),
                "credit_in_account_currency": acc2_amount,
                "custom_reference_type": source_doc.doctype,
                "custom_reference_name": source_doc.name,
            },
        ],
    )
    je.save()
    if kwargs.get("submit"):
        je.submit()
    return je
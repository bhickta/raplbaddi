import datetime
from raplbaddi.supportrapl.doctype.customer_support_settings.customer_support_settings import items_eligible_for_complaints

def get_context(context):
    context.today = datetime.datetime.today().date()
    context.items_eligible_for_complaints = items_eligible_for_complaints()
    return context
from .itemwise_report import ItemwiseOrderAndShortageReport
from .orderwise_report import OrderAndShortageReport

def execute(filters=None):
    filters = filters or {}
    report_type = filters.get("report_type")
    
    if report_type == "Itemwise Order and Shortage":
        return ItemwiseOrderAndShortageReport(filters).run()
    elif report_type == "Order and Shortage":
        return OrderAndShortageReport(filters).run()
    else:
        return [], []
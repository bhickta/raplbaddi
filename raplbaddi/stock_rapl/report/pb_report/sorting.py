from raplbaddi.utils.report_utils import SortStrategy

class BoxProductionSort(SortStrategy):
    def sort(self, data):
        return sorted(data, key=lambda x: x.get('short_qty', 0), reverse=True)

class BoxDispatchSort(SortStrategy):
    def sort(self, data):
        return sorted(data, key=lambda x: x.get('dispatch_need_to_complete_so', 0), reverse=True)

class DeadStockSort(SortStrategy):
    def sort(self, data):
        return sorted([item for item in data if item.get('dead_inventory', 0) > 0 and item.get('total_stock', 0) > 0],
                      key=lambda x: x.get('total_stock', 0), reverse=True)

class UrgentDispatchSort(SortStrategy):
    def sort(self, data):
        return sorted([item for item in data if item.get('urgent_dispatch', 0) > 0],
                      key=lambda x: x.get('urgent_dispatch_pending', 0), reverse=True)

class BoxStockSort(SortStrategy):
    def __init__(self, central_stock_key):
        self.central_stock_key = central_stock_key

    def sort(self, data):
        return sorted([item for item in data if item.get(self.central_stock_key, 0) > 0],
                      key=lambda x: x.get(self.central_stock_key, 0), reverse=True)
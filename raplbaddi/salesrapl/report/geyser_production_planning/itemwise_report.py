from .base_report import BaseReport
from raplbaddi.utils import report_utils
from raplbaddi.salesrapl.report.geyser_production_planning import sales_order_data

class ItemwiseOrderAndShortageReport(BaseReport):
    def run(self):
        data = sales_order_data.get_so_items(self.filters)
        bin_stock = sales_order_data.get_bin_stock()
        box_stock = sales_order_data.get_box_qty()
        ordered_boxes = self.get_ordered_box_qty()

        for row in data:
            row["brand"] = row["brand"].replace("- RAPL", "")
            row["item_name"] = f"{row['item_code']} {row['brand']}"
            self._enrich_with_stock(row, bin_stock)
            self._enrich_with_box(row, box_stock)
            row["unit"] = self.set_item_unit(row["item_code"])
            self._enrich_with_ordered_box(row, ordered_boxes)
            row["city"] = self.get_city_from_shipping(row.get("shipping_address_name"))
            row["box_short_qty"] = (
                row.get("short_qty", 0) - row.get("box_order", 0) - row.get("box_stock_qty", 0)
            )

        self.count_cities(data)
        data.sort(key=lambda x: x.get("%", 0), reverse=True)
        self.remove_delivered_items(data)
        return self._build_columns(), data
    
    def remove_delivered_items(self, data):
        if self.filters.get("is_show_delivered_items"):
            return
        data[:] = [row for row in data if row["pending_qty"] != 0]


    def _enrich_with_stock(self, row, bin_stock):
        for b in bin_stock:
            if b["item_code"] == row["item_code"] and b["warehouse"].replace("- RAPL", "") == row["brand"]:
                short = max(0, row["pending_qty"] - b["actual_qty"])
                row["%"] = 100 - (short / row["pending_qty"]) * 100 if row["pending_qty"] else 0
                row["actual_qty"] = b["actual_qty"]
                row["short_qty"] = short
                break

    def _enrich_with_box(self, row, box_stock):
        for box in box_stock:
            if box.get("box") == row.get("box"):
                row["box_stock_qty"] = box["warehouse_qty"]
                break

    def _enrich_with_ordered_box(self, row, ordered_boxes):
        box_detail = ordered_boxes.get(row.get("box"), {})
        row["box_order"] = box_detail.get("ordered", 0)
        row["supplier"] = box_detail.get("supplier")

    def _build_columns(self):
        builder = report_utils.ColumnBuilder()
        return builder \
            .add_column("Order Date", "Date", 100, "date") \
            .add_column("Planning Remarks", "HTML", 100, "planning_remarks") \
            .add_column("Dispatch Remarks", "HTML", 100, "dispatch_remarks") \
            .add_column("SO Number", "Link", 100, "sales_order", options="Sales Order") \
            .add_column("City", "Data", 100, "city") \
            .add_column("City Count", "Int", 100, "city_count") \
            .add_column("Customer", "Link", 300, "customer", options="Customer") \
            .add_column("Item", "Data", 100, "item_code") \
            .add_column("Brand", "Data", 100, "brand") \
            .add_column("Color", "Data", 100, "color") \
            .add_column("Order Qty", "Int", 120, "ordered_qty") \
            .add_column("Pending Qty", "Int", 120, "pending_qty") \
            .add_column("Delivered Qty", "Int", 120, "delivered_qty") \
            .add_column("Actual Qty", "Int", 120, "actual_qty") \
            .add_column("Short Qty", "Int", 120, "short_qty") \
            .add_column("Item Name", "Data", 130, "item_name") \
            .add_column("SO Remark", "HTML", 130, "so_remarks") \
            .add_column("Box name", "Link", 100, "box", options="Item") \
            .add_column("Box Qty", "Int", 120, "box_stock_qty") \
            .add_column("Box Shortage", "Int", 120, "box_short_qty") \
            .add_column("Box Order", "HTML", 130, "box_order") \
            .add_column("Supplier", "Data", 120, "supplier") \
            .add_column("Unit", "Data", 130, "unit") \
            .build()

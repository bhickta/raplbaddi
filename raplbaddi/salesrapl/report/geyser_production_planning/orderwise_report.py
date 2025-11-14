from .base_report import BaseReport
from raplbaddi.utils import report_utils
from raplbaddi.salesrapl.report.geyser_production_planning import sales_order_data

class OrderAndShortageReport(BaseReport):
    def run(self):
        raw_data = sales_order_data.get_so_items(self.filters)
        so_mapped = report_utils.accum_mapper(data=raw_data, key="sales_order")
        bin_stock = sales_order_data.get_bin_stock()
        data = []

        for so, items in so_mapped.items():
            entry = self._build_summary(so, items, bin_stock)
            data.append(entry)

        self.count_cities(data)
        data.sort(key=lambda x: x.get("%", 0), reverse=True)
        return self._build_columns(), data

    def _build_summary(self, so, items, bin_stock):
        entry = {
            "sales_order": so,
            "pending_qty": 0,
            "ordered_qty": 0,
            "so_shortage": 0,
            "items": set(),
            "brands": set(),
        }

        for item in items:
            entry.update({
                "city": self.get_city_from_shipping(item.get("shipping_address_name")),
                "status": item["status"],
                "planning_remarks": item["planning_remarks"],
                "remarks_unit_1": item["remarks_unit_1"],
                "remarks_unit_2": item["remarks_unit_2"],
                "so_remarks": item["so_remarks"],
                "date": item["date"],
                "customer": item["customer"],
                "customer_name": item["customer_name"],
                "color": item["color"]
            })
            entry["pending_qty"] += item["pending_qty"]
            entry["billing_rule"] = item.get("billing_rule") or "None"
            entry["ordered_qty"] += item["ordered_qty"]
            entry["items"].add(item["item_code"])
            entry["brands"].add(item["brand"].replace(" - RAPL", ""))

            for b in bin_stock:
                if b["item_code"] == item["item_code"] and b["warehouse"] == item["brand"]:
                    short = max(0, item["pending_qty"] - b["actual_qty"])
                    entry["so_shortage"] += short

        entry["items"] = ', '.join(entry["items"])
        entry["brands"] = ', '.join(entry["brands"])
        entry["%"] = 100 - (entry["so_shortage"] / entry["pending_qty"]) * 100 if entry["pending_qty"] else 0
        return entry

    def _build_columns(self):
        builder = report_utils.ColumnBuilder()
        return builder \
            .add_column("Date", "Date", 100, "date") \
            .add_column("Items", "Data", 100, "items") \
            .add_column("Planning Remarks", "HTML", 100, "planning_remarks") \
            .add_column("Remarks Unit 1", "HTML", 100, "remarks_unit_1") \
            .add_column("Remarks Unit 2", "HTML", 100, "remarks_unit_2") \
            .add_column("Billing Rule", "Data", 120, "billing_rule") \
            .add_column("Sales Order", "Link", 100, "sales_order", options="Sales Order") \
            .add_column("City", "Data", 100, "city") \
            .add_column("City Count", "Int", 100, "city_count") \
            .add_column("Customer", "Link", 300, "customer", options="Customer") \
            .add_column("Pending Qty", "Int", 120, "pending_qty") \
            .add_column("Shortage Qty", "Int", 100, "so_shortage") \
            .add_column("% Available", "Int", 100, "%", disable_total=True) \
            .add_column("Brand", "Data", 100, "brands") \
            .add_column("SO Remark", "HTML", 130, "so_remarks") \
            .build()
            # .add_column("Status", "Data", 100, "status") \
            # .add_column("Ordered Qty", "Int", 120, "pending_qty") \

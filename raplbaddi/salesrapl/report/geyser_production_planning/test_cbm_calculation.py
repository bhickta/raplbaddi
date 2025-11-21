
import unittest
from unittest.mock import MagicMock, patch
from raplbaddi.salesrapl.report.geyser_production_planning import itemwise_report, orderwise_report

class TestCBMCalculation(unittest.TestCase):
    def test_itemwise_cbm(self):
        # Mock data
        mock_data = [
            {
                "item_code": "ITEM-1",
                "brand": "BrandA - RAPL",
                "pending_qty": 10,
                "cbm": 0.5,
                "shipping_address_name": "Address 1",
                "status": "Pending",
                "planning_remarks": "",
                "remarks_unit_1": "",
                "remarks_unit_2": "",
                "so_remarks": "",
                "date": "2023-01-01",
                "customer": "Cust1",
                "customer_name": "Customer 1",
                "color": "Red",
                "billing_rule": "Rule1",
                "ordered_qty": 10,
                "box": "Box1"
            }
        ]
        
        with patch('raplbaddi.salesrapl.report.geyser_production_planning.sales_order_data.get_so_items', return_value=mock_data), \
             patch('raplbaddi.salesrapl.report.geyser_production_planning.sales_order_data.get_bin_stock', return_value=[]), \
             patch('raplbaddi.salesrapl.report.geyser_production_planning.sales_order_data.get_box_qty', return_value=[]), \
             patch.object(itemwise_report.ItemwiseOrderAndShortageReport, 'get_ordered_box_qty', return_value={}), \
             patch.object(itemwise_report.ItemwiseOrderAndShortageReport, 'set_item_unit', return_value="Unit1"), \
             patch.object(itemwise_report.ItemwiseOrderAndShortageReport, 'get_city_from_shipping', return_value="City1"), \
             patch.object(itemwise_report.ItemwiseOrderAndShortageReport, 'count_cities'):

            report = itemwise_report.ItemwiseOrderAndShortageReport({})
            columns, data = report.run()
            
            self.assertEqual(data[0]['total_cbm'], 5.0)
            print("Itemwise CBM Verified: 10 * 0.5 = 5.0")

    def test_orderwise_cbm(self):
        # Mock data
        mock_data = [
            {
                "sales_order": "SO-1",
                "item_code": "ITEM-1",
                "brand": "BrandA - RAPL",
                "pending_qty": 10,
                "cbm": 0.5,
                "shipping_address_name": "Address 1",
                "status": "Pending",
                "planning_remarks": "",
                "remarks_unit_1": "",
                "remarks_unit_2": "",
                "so_remarks": "",
                "date": "2023-01-01",
                "customer": "Cust1",
                "customer_name": "Customer 1",
                "color": "Red",
                "billing_rule": "Rule1",
                "ordered_qty": 10
            },
            {
                "sales_order": "SO-1",
                "item_code": "ITEM-2",
                "brand": "BrandA - RAPL",
                "pending_qty": 5,
                "cbm": 2.0,
                "shipping_address_name": "Address 1",
                "status": "Pending",
                "planning_remarks": "",
                "remarks_unit_1": "",
                "remarks_unit_2": "",
                "so_remarks": "",
                "date": "2023-01-01",
                "customer": "Cust1",
                "customer_name": "Customer 1",
                "color": "Blue",
                "billing_rule": "Rule1",
                "ordered_qty": 5
            }
        ]

        with patch('raplbaddi.salesrapl.report.geyser_production_planning.sales_order_data.get_so_items', return_value=mock_data), \
             patch('raplbaddi.salesrapl.report.geyser_production_planning.sales_order_data.get_bin_stock', return_value=[]), \
             patch.object(orderwise_report.OrderAndShortageReport, 'get_city_from_shipping', return_value="City1"), \
             patch.object(orderwise_report.OrderAndShortageReport, 'count_cities'):

            report = orderwise_report.OrderAndShortageReport({})
            columns, data = report.run()
            
            # Total CBM = (10 * 0.5) + (5 * 2.0) = 5.0 + 10.0 = 15.0
            self.assertEqual(data[0]['total_cbm'], 15.0)
            print("Orderwise CBM Verified: (10 * 0.5) + (5 * 2.0) = 15.0")

if __name__ == '__main__':
    unittest.main()

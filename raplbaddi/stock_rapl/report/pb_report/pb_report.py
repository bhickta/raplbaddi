# Copyright (c) 2023, Nishant Bhickta and contributors
# For license information, please see license.txt

import frappe
from raplbaddi.utils import report_utils
from raplbaddi.stock_rapl.report.pb_report.box_data import BoxRequirements
from .sorting import (
    BoxProductionSort,
    BoxDispatchSort,
    DeadStockSort,
    UrgentDispatchSort,
    BoxStockSort
)

# Initialize data source
box_data_source = BoxRequirements()

# --- Central Location Configuration ---
class LocationConfig:
    """
    Configuration for a data location (warehouse or supplier).
    Manages properties and standard key generation for each location.
    """
    def __init__(self, id, display_name, short_code, warehouse_fetch_name, data_source_name=None, has_projected_qty=False):
        self.id = id
        self.display_name = display_name
        self.short_code = short_code
        self.warehouse_fetch_name = warehouse_fetch_name
        self.data_source_name = data_source_name # Name for fetching MR/PO/Priority if it's a supplier
        self.has_projected_qty = has_projected_qty

    def is_supplier(self):
        """Checks if this location is a supplier (has MR/PO/Priority data)."""
        return bool(self.data_source_name)

    # --- Key Generation Methods for standardized data dictionary keys ---
    def stock_key(self): return f'stock_{self.id}'
    def projected_key(self): return f'projected_{self.id}'
    def paper_stock_key(self): return f'{self.id}_paper_stock'
    def production_key(self): return f'production_{self.id}'
    def dispatch_key(self): return f'dispatch_{self.id}'
    def po_name_key(self): return f'po_name_{self.id}'
    def remain_prod_key(self): return f'remain_prod_{self.id}'
    def mr_key(self): return f'mr_{self.id}'
    def priority_key(self): return f'priority_{self.id}'

LOCATIONS_CONFIG = [
    LocationConfig(
        id='rapl',
        display_name='RAPL',
        short_code='RL',
        warehouse_fetch_name='Packing Boxes - Rapl',
        has_projected_qty=True
    ),
    LocationConfig(
        id='jai',
        display_name='JAI',
        short_code='J',
        warehouse_fetch_name='Jai Ambey Industries - RAPL',
        data_source_name='Jai Ambey Industries'
    ),
    LocationConfig(
        id='amit',
        display_name='Amit',
        short_code='A',
        warehouse_fetch_name="Amit Print 'N' Pack - RAPL",
        data_source_name="Amit Print 'N' Pack"
    ),
    LocationConfig(
        id='rana',
        display_name='Rana',
        short_code='R',
        warehouse_fetch_name="Rana, Packing Box - RAPL",
        data_source_name="Rana, Packing Box"
    ),
]

# Helper to safely get data from nested dictionaries
def get_nested_value(data_dict, primary_key, secondary_key, default=0.0):
    return data_dict.get(primary_key, {}).get(secondary_key, default)

def get_warehouse_data(warehouse_name):
    # Consider adding caching here if warehouse_qty is expensive and called multiple times
    warehouse_data_list = box_data_source.warehouse_qty(warehouse=warehouse_name)
    return {item['box']: item for item in warehouse_data_list}


class SortStrategyFactory:
    @staticmethod
    def get_strategy(report_type):
        rapl_config = next((loc for loc in LOCATIONS_CONFIG if loc.id == 'rapl'), None)
        # Fallback key if RAPL config is somehow not found (should not happen)
        rapl_stock_key = rapl_config.stock_key() if rapl_config else 'stock_rapl'

        strategies = {
            'Box Production': BoxProductionSort(),
            'Box Dispatch': BoxDispatchSort(),
            'Dead Stock': DeadStockSort(),
            'Urgent Dispatch': UrgentDispatchSort(),
            'Box Stock': BoxStockSort(central_stock_key=rapl_stock_key)
        }
        return strategies.get(report_type)

# --- Data Joining and Processing ---
def join_data_processing(filters=None):
    all_boxes_list = box_data_source.all_boxes('Packing Boxes', 'box')
    all_paper_list = box_data_source.all_boxes('Packing Paper', 'paper')
    all_paper_map = {paper_item['paper']: paper_item for paper_item in all_paper_list}
    so_map = report_utils.get_mapped_data(data=box_data_source.get_box_requirement_from_so(), key='box')

    all_location_data_cache = _fetch_all_location_data_cache()
    processed_boxes = [
        _process_box_item(
            box_item,
            all_paper_map,
            so_map,
            all_location_data_cache
        )
        for box_item in all_boxes_list
    ]

    rapl_central_config = next((loc for loc in LOCATIONS_CONFIG if loc.id == 'rapl'), None)
    for box_data_row in processed_boxes:
        _add_calculated_fields(box_data_row, rapl_central_config)

    report_type = filters.get('report_type') if filters else None
    strategy = SortStrategyFactory.get_strategy(report_type)
    return strategy.sort(data=processed_boxes) if strategy else processed_boxes


def _fetch_all_location_data_cache():
    cache = {}
    for loc_config in LOCATIONS_CONFIG:
        mr_data, po_data, priority_data = {}, {}, {}
        if loc_config.is_supplier():
            source_name = loc_config.data_source_name
            mr_data = report_utils.get_mapped_data(
                data=box_data_source.get_box_order_for_production(source_name), key='box'
            )
            po_data = report_utils.get_mapped_data(
                data=box_data_source.get_supplierwise_po(source_name), key='box'
            )
            priority_data = report_utils.get_mapped_data(
                data=box_data_source.get_paper_supplier_priority(source_name), key='box'
            )
        cache[loc_config.id] = {
            'warehouse': get_warehouse_data(loc_config.warehouse_fetch_name),
            'mr': mr_data,
            'po': po_data,
            'priority': priority_data,
            'config': loc_config
        }
    return cache


def _process_box_item(box_item, all_paper_map, so_map, all_location_data_cache):
    current_box_data = box_item.copy()
    box_name = current_box_data.get('box', '-')

    current_box_data['so_qty'] = get_nested_value(so_map, box_name, 'so_qty')
    current_box_data['so_name'] = get_nested_value(so_map, box_name, 'so_name', '')

    box_particular = current_box_data.get('box_particular', '')
    paper_name_suffix = current_box_data.get('paper_name', '')
    full_paper_item_name = f'PP {box_particular} {paper_name_suffix}' if box_particular and paper_name_suffix else ''
    current_box_data['paper'] = all_paper_map.get(full_paper_item_name, {}).get('paper')

    for loc_id, loc_data_bundle in all_location_data_cache.items():
        loc_config = loc_data_bundle['config']
        loc_warehouse_map = loc_data_bundle['warehouse']

        current_box_data[loc_config.stock_key()] = get_nested_value(loc_warehouse_map, box_name, 'warehouse_qty')
        if loc_config.has_projected_qty:
            current_box_data[loc_config.projected_key()] = get_nested_value(loc_warehouse_map, box_name, 'projected_qty')

        if current_box_data['paper']:
            current_box_data.setdefault(loc_config.paper_stock_key(), 0.0)
            current_box_data[loc_config.paper_stock_key()] = get_nested_value(
                loc_warehouse_map, current_box_data['paper'], 'warehouse_qty'
            )

        if loc_config.is_supplier():
            loc_mr_map = loc_data_bundle['mr']
            loc_po_map = loc_data_bundle['po']
            loc_priority_map = loc_data_bundle['priority']

            current_box_data[loc_config.production_key()] = get_nested_value(loc_mr_map, box_name, 'qty')
            current_box_data[loc_config.dispatch_key()] = get_nested_value(loc_po_map, box_name, 'box_qty')
            current_box_data[loc_config.po_name_key()] = get_nested_value(loc_po_map, box_name, 'po_name', '')
            received_qty = get_nested_value(loc_mr_map, box_name, 'received_qty')
            current_box_data[loc_config.remain_prod_key()] = current_box_data[loc_config.production_key()] - received_qty
            current_box_data[loc_config.mr_key()] = get_nested_value(loc_mr_map, box_name, 'mr_name', '')
            current_box_data[loc_config.priority_key()] = get_nested_value(loc_priority_map, box_name, 'priority')
    return current_box_data


def _add_calculated_fields(box_data_row, rapl_central_config):
    all_stocks_sum = sum(box_data_row.get(loc.stock_key(), 0.0) for loc in LOCATIONS_CONFIG)
    all_production_sum = sum(
        box_data_row.get(loc.production_key(), 0.0) for loc in LOCATIONS_CONFIG if loc.is_supplier()
    )
    all_dispatch_sum = sum(
        box_data_row.get(loc.dispatch_key(), 0.0) for loc in LOCATIONS_CONFIG if loc.is_supplier()
    )

    msl = box_data_row.get('msl', 0.0)
    rapl_msl_val = box_data_row.get('rapl_msl', 0.0)
    so_qty_val = box_data_row.get('so_qty', 0.0)

    stock_at_rapl_central = box_data_row.get(rapl_central_config.stock_key(), 0.0) if rapl_central_config else 0.0

    target_inventory_for_shortage = so_qty_val + msl
    current_total_inventory_for_shortage = all_stocks_sum + all_production_sum
    box_data_row['short_qty'] = max(0, target_inventory_for_shortage - current_total_inventory_for_shortage)
    box_data_row['over_stock_qty'] = min(0, target_inventory_for_shortage - current_total_inventory_for_shortage)

    target_dispatch_need = rapl_msl_val + so_qty_val
    current_dispatchable = stock_at_rapl_central + all_dispatch_sum
    box_data_row['dispatch_need_to_complete_so'] = max(0, target_dispatch_need - current_dispatchable)
    box_data_row['total_stock'] = all_stocks_sum
    box_data_row['urgent_dispatch'] = max(0, so_qty_val - stock_at_rapl_central)
    box_data_row['urgent_dispatch_pending'] = max(0, so_qty_val - stock_at_rapl_central - all_dispatch_sum)

# --- Column Definition Helpers ---
def _add_common_cols(builder):
    builder.add_column("D", "Check", 40, "dead_inventory")
    builder.add_column("Item", "Link", 180, "box", options="Item")
    return builder

def _add_location_specific_cols(builder, col_configs):
    """Generic helper to add columns based on location configurations."""
    for loc in LOCATIONS_CONFIG:
        for col_config in col_configs:
            if col_config.get("condition", lambda l: True)(loc): # Optional condition
                label = col_config["label_format"].format(loc.display_name, loc.short_code)
                fieldtype = col_config["fieldtype"]
                width = col_config["width"]
                fieldname = col_config["fieldname_format"].format(loc.id)
                options = col_config.get("options")
                disable_total = col_config.get("disable_total")
                builder.add_column(label, fieldtype, width, fieldname, options=options, disable_total=disable_total)
    return builder

def _add_priority_cols(builder):
    col_configs = [{
        "label_format": "{}", # Uses short_code directly
        "fieldtype": "Int", "width": 20,
        "fieldname_format": LocationConfig(id='{}', display_name='', short_code='', warehouse_fetch_name='').priority_key(), # Get format from an instance
        "condition": lambda loc: loc.is_supplier()
    }]
    # Special handling for label_format to use loc.short_code
    for loc in LOCATIONS_CONFIG:
        if loc.is_supplier():
            builder.add_column(loc.short_code, "Int", 20, loc.priority_key())
    return builder


def _add_links_cols(builder):
    builder.add_column("SOs", "HTML", 100, "so_name")
    col_configs = [
        {"label_format": "MR {}", "fieldtype": "HTML", "width": 100, "fieldname_format": LocationConfig(id='{}',display_name='',short_code='',warehouse_fetch_name='').mr_key(), "condition": lambda loc: loc.is_supplier()},
        {"label_format": "POs {}", "fieldtype": "HTML", "width": 100, "fieldname_format": LocationConfig(id='{}',display_name='',short_code='',warehouse_fetch_name='').po_name_key(), "condition": lambda loc: loc.is_supplier()},
    ]
    return _add_location_specific_cols(builder, col_configs)

def _add_prod_cols(builder):
    col_configs = [{
        "label_format": "{} Prod", "fieldtype": "Int", "width": 80, "fieldname_format": LocationConfig(id='{}',display_name='',short_code='',warehouse_fetch_name='').production_key(),
        "condition": lambda loc: loc.is_supplier()
    }]
    return _add_location_specific_cols(builder, col_configs)

def _add_dispatch_cols(builder):
    col_configs = [{
        "label_format": "{} Disp", "fieldtype": "Int", "width": 90, "fieldname_format": LocationConfig(id='{}',display_name='',short_code='',warehouse_fetch_name='').dispatch_key(),
        "condition": lambda loc: loc.is_supplier()
    }]
    return _add_location_specific_cols(builder, col_configs)

def _add_stock_cols(builder):
    # Add individual stock columns
    for loc in LOCATIONS_CONFIG:
        builder.add_column(f"{loc.display_name} Stock", "Int", 100, loc.stock_key())
        if loc.has_projected_qty:
            builder.add_column(f"Projected {loc.display_name}", "Int", 100, loc.projected_key())
    # Add overall total stock
    builder.add_column("Total Stock", "Int", 120, "total_stock")
    return builder

def _add_paper_cols(builder):
    builder.add_column("Paper", "Link", 180, "paper", options="Item")
    col_configs = [{
        "label_format": "{} Paper", "fieldtype": "Int", "width": 100, "fieldname_format": LocationConfig(id='{}',display_name='',short_code='',warehouse_fetch_name='').paper_stock_key(),
        "disable_total": "True" # Note: disable_total expects a string "True" or "False" usually in Frappe
    }]
    return _add_location_specific_cols(builder, col_configs)

# Simple column adders remain unchanged
def _add_urgent_dispatch_columns(builder):
    builder.add_column("Urgent Dispatch", "Int", 120, "urgent_dispatch")
    builder.add_column("Order Pending", "Int", 120, "urgent_dispatch_pending")
    return builder

def _add_dispatch_need_column(builder):
    builder.add_column("Dispatch Need", "Int", 120, "dispatch_need_to_complete_so")
    return builder

def _add_shortage_column(builder):
    builder.add_column("Shortage", "Int", 100, "short_qty")
    return builder

def _add_so_column(builder):
    builder.add_column("SO", "Int", 80, "so_qty")
    return builder

def _add_box_msl_column(builder):
    builder.add_column("MSL", "Int", 80, "msl")
    return builder

def _add_rapl_msl_column(builder):
    builder.add_column("Rapl MSL", "Int", 80, "rapl_msl")
    return builder

def _add_over_stock_column(builder):
    builder.add_column("Over Stock", "Int", 100, "over_stock_qty")
    return builder

# --- Main Columns Function ---
def define_columns(filters=None):
    filters = filters or {}
    builder = report_utils.ColumnBuilder()
    report_type = filters.get('report_type')

    # Report-type specific columns
    if report_type == 'Box Stock':
        _add_common_cols(builder)
    elif report_type == 'Box Production':
        _add_common_cols(builder)
        _add_box_msl_column(builder)
        _add_prod_cols(builder)
        _add_shortage_column(builder)
    elif report_type == 'Box Dispatch':
        _add_common_cols(builder)
        _add_so_column(builder)
        _add_rapl_msl_column(builder)
        _add_dispatch_cols(builder)
        _add_dispatch_need_column(builder)
    elif report_type == 'Dead Stock':
        _add_common_cols(builder)
    elif report_type == 'Urgent Dispatch':
        _add_common_cols(builder)
        _add_so_column(builder)
        _add_dispatch_cols(builder)
        _add_urgent_dispatch_columns(builder)
    else: # Default set of columns
        _add_common_cols(builder)

    # General columns added based on filters
    if filters.get('box_stock'): # Consider renaming filter keys for clarity e.g., 'show_stock_summary'
        _add_stock_cols(builder)
    if filters.get('paper_stock'):
        _add_paper_cols(builder)
    if filters.get('over_stock'):
        _add_over_stock_column(builder)
    if filters.get('add_links'):
        _add_links_cols(builder)
    if filters.get('add_priority'):
        _add_priority_cols(builder)

    return builder.build()

# --- Main Execution Function ---
def execute(filters=None):
    data = join_data_processing(filters) # Data processing first
    cols = define_columns(filters)       # Then define columns
    return cols, data
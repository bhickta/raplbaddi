from .config import (LocationConfig, LOCATIONS_CONFIG)
from raplbaddi.utils.report_utils import ColumnBuilder

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
    builder = ColumnBuilder()
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
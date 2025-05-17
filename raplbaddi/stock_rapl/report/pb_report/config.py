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
from frappe.model.document import Document

class ProductionDocItem(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        item_code: DF.Link | None
        operator_name: DF.Link | None
        operation_name: DF.Link | None
        start_time: DF.Time | None
        end_time: DF.Time | None
        breakdown_time: DF.Float
        standard_production_100: DF.Float
        standard_production_80: DF.Float
        actual_production: DF.Float
        manpower: DF.Int
        cycle_time: DF.Int
        
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data

    # end: auto-generated types
    pass

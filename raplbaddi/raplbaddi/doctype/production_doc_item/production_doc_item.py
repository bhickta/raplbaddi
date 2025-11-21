from frappe.model.document import Document

class ProductionDocItem(Document):
    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        actual_production: DF.Float
        breakdown_time: DF.Float
        end_time: DF.Time | None
        item_code: DF.Link | None
        manpower: DF.Int
        operator_name: DF.Data | None
        parent: DF.Data
        parentfield: DF.Data
        parenttype: DF.Data
        standard_production_100: DF.Float
        standard_production_80: DF.Float
        start_time: DF.Time | None
    # end: auto-generated types
    pass

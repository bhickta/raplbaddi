import frappe

def execute():
    return
    # This query updates 'tabItem' to set 'disabled = 1' (disabled) for items
    # that meet the following criteria:
    # 1. They are currently NOT disabled (disabled = 0).
    # 2. Their item_group is NOT 'Tools, Hardware and Maintenance' or 'Consumable'.
    # 3. The item is NOT listed in the subquery (i.e., it is neither a BOM component nor a BOM finished item).

    query = """
        UPDATE `tabItem`
        SET disabled = 1
        WHERE disabled = 0
          AND item_group NOT IN ('Tools, Hardware and Maintenance', 'Consumable')
          AND name NOT IN (
              -- Subquery to get a list of all items involved in COMMITTED BOMs (docstatus = 1)
              SELECT item_code
              FROM `tabBOM Item` bi
              INNER JOIN `tabBOM` b ON b.name = bi.parent
              WHERE b.docstatus = 1
              -- Union with the new requirement: items for which a BOM is created
              UNION
              SELECT item
              FROM `tabBOM`
              WHERE docstatus = 1
          )
    """

    frappe.db.sql(query)
    frappe.db.commit()

    frappe.msgprint("Item disabling process completed.")
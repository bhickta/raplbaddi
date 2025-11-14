import frappe


def set_day():
    query = """
        UPDATE `tabAttendance Rapl Item`
        SET day = ELT(DAYOFWEEK(`date`), 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday')
    """
    frappe.db.sql(query)

def set_holiday():
    query = """
        UPDATE `tabAttendance Rapl Item`
        SET is_holiday = CASE
            WHEN day = 'Sunday' OR date = '2025-03-14' THEN 1
            ELSE 0
        END
    """
    frappe.db.sql(query)

def execute():
    set_day()
    set_holiday()
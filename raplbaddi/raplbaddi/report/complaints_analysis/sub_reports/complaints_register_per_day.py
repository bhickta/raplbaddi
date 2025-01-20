import frappe
from raplbaddi.raplbaddi.report.utils.service_centre import ServiceCentreReport

class ComplaintsRegisterPerDay(ServiceCentreReport):
    def __init__(self, filters=None):
        super().__init__(filters)

    def fetch_data(self):
        query = """
			SELECT 
				custom_creation_date,
				COUNT(name) AS no_of_complaints
			FROM 
				tabIssueRapl
			GROUP BY 
				custom_creation_date
			ORDER BY 
				custom_creation_date DESC
		"""
        raw_data = frappe.db.sql(query, as_dict=True)

        return raw_data

    def fetch_columns(self):
        return [
            {
                "label": "Complaint Register Date",
                "fieldname": "custom_creation_date",
                "fieldtype": "Data",
                "width": 150,
            },
            {
                "label": "No of Complaints Registered",
                "fieldname": "no_of_complaints",
                "fieldtype": "Int",
                "width": 200,
            },
        ]
from frappe.model.document import Document
from datetime import datetime

class OperationEntry(Document):

    def validate(self):

        for row in self.items:

            # skip empty rows
            if not row.start_time or not row.end_time:
                continue

            cycle_time = self.cycle_time
            if not cycle_time:
                continue

            # convert string to time object
            def to_time(val):
                if isinstance(val, str):
                    try:
                        return datetime.strptime(val, "%H:%M:%S").time()
                    except:
                        return datetime.strptime(val, "%H:%M").time()
                return val

            start_time = to_time(row.start_time)
            end_time = to_time(row.end_time)

            # combine into datetime
            start = datetime.combine(datetime.today(), start_time)
            end = datetime.combine(datetime.today(), end_time)

            # total working seconds
            total_seconds = (end - start).total_seconds()

            # breakdown in seconds
            breakdown_seconds = (row.breakdown_time or 0) * 60

            available_time = total_seconds - breakdown_seconds

            if available_time > 0:
                row.standard_production_100 = available_time / cycle_time
                row.standard_production_80 = row.standard_production_100 * 0.80
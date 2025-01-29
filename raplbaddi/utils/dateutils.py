import datetime

def get_first_day_of_week(date):
    """Returns the first day (Monday) of the week for a given date."""
    return date - datetime.timedelta(days=date.weekday())

def get_last_day_of_week(date):
    """Returns the last day (Sunday) of the week for a given date."""
    return date + datetime.timedelta(days=(6 - date.weekday()))
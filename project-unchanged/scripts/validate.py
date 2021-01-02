from datetime import date, datetime

def validate_date_range(from_date, to_date):
    from_date = date.fromisoformat(from_date)
    to_date = date.fromisoformat(to_date)
    return (to_date and from_date) and (from_date <= to_date)

def validate_date_time_range(from_date_time, to_date_time):
    from_date_time = datetime.fromisoformat(from_date_time)
    to_date_time = datetime.fromisoformat(to_date_time)
    return (to_date_time and from_date_time) and (from_date_time <= to_date_time)

def validate_num_range(min_value, max_value):
    min_value = int(min_value)
    max_value = int(max_value)
    return (min_value != None and max_value != None) and (min_value <= max_value)
from datetime import datetime, time
from django.http import JsonResponse
from rest_framework.decorators import api_view

def convert_to_hms(time_str):
    if isinstance(time_str, time):
        return time_str.strftime('%H:%M:%S')
    
    time_formats = [
        '%H:%M:%S',  # 14:30:00
        '%H:%M',     # 14:30
    ]

    for fmt in time_formats:
        try:
            parsed_time = datetime.strptime(time_str, fmt)
            return parsed_time.strftime('%H:%M:%S')
        except ValueError:
            continue

    raise ValueError(f"Time format not recognized: {time_str}")

def is_valid_time(time_str):
    try:
        datetime.strptime(time_str, '%H:%M:%S')
        return True
    except ValueError:
        try:
            datetime.strptime(time_str, '%H:%M')
            return True
        except ValueError:
            return False

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
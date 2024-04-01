import datetime as dt
from timezonefinder import TimezoneFinder
import pytz

def local_time(latitude, longitude):
    current_time_utc = dt.datetime.now(pytz.utc)
    tz = TimezoneFinder()  # Timezone
    timezone_str = tz.timezone_at(lat=latitude, lng=longitude)  # Timezone string

    # Local timezone object
    local_timezone = pytz.timezone(timezone_str)

    # Convert the current time to the local time of the specified location
    current_time_local = current_time_utc.astimezone(local_timezone)
    current_hour_and_minutes = current_time_local.strftime('%H:%M')
    current_hour_only = current_time_local.strftime('%H')

    return current_time_local, current_hour_and_minutes, current_hour_only

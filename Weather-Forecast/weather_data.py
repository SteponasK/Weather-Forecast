import datetime as dt
from metno_locationforecast import Place, Forecast
from symbols import choose_weather_symbol
from local_time import local_time

def fetch_weather_data(city_name, latitude, longitude):
    city = Place(city_name, latitude, longitude)
    # Compact - gives less information
    city_forecast = Forecast(city, "Weather Forecast Application https://github.com/SteponasK", "compact") 
    city_forecast.update()

    current_time_local, current_hour, current_hour_only = local_time(latitude, longitude)
    current_hour_intervals = [interval for interval in city_forecast.data.intervals if current_time_local.hour == interval.start_time.hour]

    # Weather parameters
    parameters = {
        "wind_speed": "",
        "air_pressure": "",
        "relative_humidity": "",
        "precipitation_amount": "",
        "precipitation_amount_total": ""
    }

    if current_hour_intervals:
        current_hour_interval = current_hour_intervals[0]
        variables = current_hour_interval.variables

        parameters.update({
            "wind_speed": f"{variables['wind_speed'].value}",
            "air_pressure": f"{variables['air_pressure_at_sea_level'].value}",
            "relative_humidity": f"{variables['relative_humidity'].value}",
            "precipitation_amount": f"{variables['precipitation_amount'].value}",
            "temperature": f"{variables['air_temperature'].value}",
            "cloud_fraction": f"{variables['cloud_area_fraction'].value}"
        })

    else:
        print("No weather data available for the current hour.")

    # Sum of all precipitation amount today
    precipitation_amount_total = sum(
        interval.variables.get("precipitation_amount", 0).value
        for interval in city_forecast.data.intervals
        if current_time_local.date() == interval.start_time.date()
           and dt.datetime.combine(current_time_local.date(), dt.time(0, 0)) <= interval.start_time <= dt.datetime.combine(current_time_local.date(), dt.time(23, 59))
    )
    precipitation_amount_total_unit = variables.get("precipitation_amount").units
    parameters["precipitation_amount_total"] = f"{precipitation_amount_total}"

    
    return parameters, current_hour, choose_weather_symbol(parameters, current_hour_only)


def choose_weather_symbol(parameters, current_hour):
    wind_speed = float(parameters['wind_speed'])  # Meters/second
    precipitation_amount = float(parameters['precipitation_amount'])  # Millimeters
    cloud_coverage = float(parameters['cloud_fraction'])  # Percentage
    current_hour = int(current_hour)

    # Choose the weather symbol based on current weather conditions
    if current_hour >= 6 and current_hour < 18:
        if precipitation_amount < 0.5:
            if cloud_coverage < 10:
                weather_situation = "clearsky_day"
            elif cloud_coverage < 25:
                weather_situation = "fair_day"
            elif cloud_coverage < 60:
                weather_situation = "partlycloudy_day"
            else:
                weather_situation = "cloudy"
        else:
            if precipitation_amount < 1.5:
                weather_situation = "lightrainshowers_day"
            elif precipitation_amount < 3:
                weather_situation = "rainshowers_day"
            else:
                weather_situation = "heavyrainshowers_day"

    else:
        if precipitation_amount < 0.5:
            if cloud_coverage < 10:
                weather_situation = "clearsky_night"
            elif cloud_coverage < 25:
                weather_situation = "fair_night"
            elif cloud_coverage < 60:
                weather_situation = "partlycloudy_night"
            else:
                weather_situation = "cloudy"
        else:
            if precipitation_amount < 1.5:
                weather_situation = "lightrainshowers_night"
            elif precipitation_amount < 3:
                weather_situation = "rainshowers_night"
            else:
                weather_situation = "heavyrainshowers_night"

    return weather_situation
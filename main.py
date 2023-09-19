import pygame
import sys
import os
import requests
from metno_locationforecast import Place, Forecast
import datetime as dt
from timezonefinder import TimezoneFinder
import pytz

# Constants
WIDTH, HEIGHT = 1280, 720
FONT_SIZE = 36

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

def fetch_weather_data(city_name, latitude, longitude):
    city = Place(city_name, latitude, longitude)
    # Compact - gives less information
    city_forecast = Forecast(city, "test application https://github.com/among_us", "compact") 
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

def get_location_info(city):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={city}"
    response = requests.get(url)
    data = response.json()
    if data:
        first_result = data[0]
        return float(first_result["lat"]), float(first_result["lon"])
    else:
        return None

def feels_like(parameters):

    # Calculations using a formula from the internet.
    c1 = -8.78469475556
    c2 = 1.61139411
    c3 = 2.33854883889
    c4 = -0.14611605
    c5 = -0.012308094
    c6 = -0.0164248277778
    c7 = 0.002211732
    c8 = 0.00072546
    c9 = -0.000003582

    T = float(parameters['temperature'])
    R = float(parameters['relative_humidity'])
    V = float(parameters['wind_speed']) * 3.6 # Convert wind speed to km/h

    heat_index = c1 + c2 * T + c3 * R + c4 * T * R + c5 * pow(T, 2) + c6 * pow(R, 2) + c7 * pow(T, 2) * R + c8 * T * pow(R, 2) + c9 * pow(T, 2) * pow(R, 2)

    wind_chill = 13.12 + 0.6215 * T - 11.37 * pow(V, 0.16) + 0.3965 * T * pow(V, 0.16)

    if wind_chill > T:
        return round(heat_index, 2)
    else:
        return round(wind_chill, 2)

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


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Weather Forecast")

    # Load background image
    background_image_path = "Resources/background.png"
    background_image = pygame.image.load(background_image_path).convert()

    # Load the search bar image
    search_bar_image_path = "Resources/search_bar.png"
    search_bar_image = pygame.image.load(search_bar_image_path).convert_alpha()

    # Photo of the information on the lower part of the screen
    info_background_path =  "Resources/info_background.png"
    info_background_image = pygame.image.load(info_background_path).convert_alpha()

    # Country/City name font
    country_name_font_path = "Resources/BebasNeue_Bold.ttf"
    country_name_text = pygame.font.Font(country_name_font_path, 42)

    # Font for descriptions and information
    info_text_font_path = "Resources/TT_Norms_Pro_Medium.otf"

    # Different sizes font for description and information
    info_text = pygame.font.Font(info_text_font_path, 29)
    city_text = pygame.font.Font(info_text_font_path, 90)
    description_text = pygame.font.Font(info_text_font_path, 55)
    temperature_text = pygame.font.Font(info_text_font_path, 130)
    feels_like_text = pygame.font.Font(info_text_font_path, 35)

    # TITLE FONT
    title_font = pygame.font.Font("Resources/Calibri_Bold.ttf", FONT_SIZE)

    # Initialize text_lines dictionary
    text_lines = {
        "city_info": "",
        "time_info": "",
    }

    # Search_bar input field size
    input_box_width = 400
    input_box_height = FONT_SIZE # pakeist sita

    # Position the Search_bar input field
    input_box_x = 195
    input_box_y = 95

    input_box = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)

    parameters = {}  
    #weather_symbol = "clear_sky"  # Default value, you can update this as needed
    city_input = ""
    text_input = ""
    current_hour = 0

    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    city_input = text_input
                    text_input = ""
                    city_input = city_input.capitalize()

                    # Get location information
                    location_info = get_location_info(city_input)

                    if location_info:
                        latitude, longitude = location_info

                        # Fetch weather data for the city
                        parameters, current_hour, weather_symbol = fetch_weather_data(city_input, latitude, longitude)

                        text_lines = {
                        "city_info": f"Current weather",
                        "time_info": current_hour
                    }
                        
                    else:
                        parameters = {}
                        text_lines = {"error": "Error: Wrong city name"}
                elif event.key == pygame.K_BACKSPACE:
                    text_input = text_input[:-1]
                else:
                    text_input += event.unicode

        # Blit the background image
        screen.blit(background_image, (0, 0))

        # Render and display the title
        title_text = title_font.render("Check weather in your area", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH // 2, 20))
        screen.blit(title_text, title_rect)

        # Render and display the text lines
        for i, (line_name, line_text) in enumerate(text_lines.items()):
            text = description_text.render(line_text, True, (0, 0, 0))
            if i == 0:
                text_rect = text.get_rect(center=(615, 320 + i * FONT_SIZE * 1.7))
            elif i == 1:
                text_rect = text.get_rect(center=(800, 320 + i * FONT_SIZE * 1.7))
            screen.blit(text, text_rect)

        # Draw the search bar
        scaled_search_bar_image = pygame.transform.scale(search_bar_image, (550, 550))
        screen.blit(scaled_search_bar_image, (input_box.x - 95, input_box.y - 147))

        # Render the current input line inside the search_bar
        input_surface = country_name_text.render(text_input, True, (153, 170, 187))
        screen.blit(input_surface, (input_box.x + 5, input_box.y + (FONT_SIZE - input_surface.get_height()) // 2))

        # Information box at the bottom of the screen
        info_background_image_surface = pygame.transform.scale(info_background_image, (962, 962))
        screen.blit(info_background_image_surface, (145, 140))

        if parameters:
            for param_name, param_value in parameters.items():
                if param_name == "wind_speed":
                    info_text_print = info_text.render(str(param_value) + "m/s", True, (191, 191, 191))
                    screen.blit(info_text_print, (168, 610))
                elif param_name == "air_pressure":
                    info_text_print = info_text.render(str(param_value) + "hPa", True, (191, 191, 191))
                    screen.blit(info_text_print, (280, 610))
                elif param_name == "relative_humidity":
                    info_text_print = info_text.render(str(param_value) + "%", True, (191, 191, 191))
                    screen.blit(info_text_print, (460, 610))
                elif param_name == "precipitation_amount":
                    info_text_print = info_text.render(str(param_value) + "mm", True, (191, 191, 191))
                    screen.blit(info_text_print, (645, 610))
                elif param_name == "precipitation_amount_total":
                    info_text_print = info_text.render(str(round(float(param_value),1)) + "mm", True, (191, 191, 191))
                    screen.blit(info_text_print, (940, 610))

            

            # Name of the city
            city_text_render = city_text.render(city_input, True, (32, 76, 129))
            screen.blit(city_text_render, (410, 200))

            # Air temperature
            temperature_render = temperature_text.render(str(round(float(parameters['temperature']))) + "\u00b0C", True, (173, 216, 230))  # (0,128,0)
            screen.blit(temperature_render, (750, 100))

            # Feels-like temperature
            feels_like_text_render = feels_like_text.render("FEELS LIKE: " + str(round(feels_like(parameters))) + "\u00b0C", True, (32, 76, 129))
            screen.blit(feels_like_text_render, (180, 520))

            # Load the weather icon 
            icon_image = pygame.image.load("Resources/Weather_Icons/" + weather_symbol + ".png")
            icon_image = pygame.transform.scale(icon_image, (200, 200))
            screen.blit(icon_image, (200, 200))

        pygame.display.flip()


if __name__ == "__main__":
    main()


import requests
def get_location_info(city):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={city}"
    response = requests.get(url)
    data = response.json()
    if data:
        first_result = data[0]
        return float(first_result["lat"]), float(first_result["lon"])
    else:
        return None

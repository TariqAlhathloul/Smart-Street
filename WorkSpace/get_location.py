import geocoder
import requests
from geopy.geocoders import Nominatim

"""
make a http request to get the current location of the raspberry pi
then extract the latitude, longitude, city
"""

def get_current_location():
    """
    No parameters.
    the function will return the [latitude, longitude] of the camera.
    """
    response = requests.get('http://ipinfo.io/json')
    data = response.json()
    if 'loc' in data:
        location = data['loc'].split(',')
        latitude = location[0]
        longitude = location[1]
        return latitude, longitude
    else:
        return None, None
def get_road_name():
    """
    No parameters.
    the function will return the road name of the camera.
    """
    latitude, longitude = get_current_location()
    geolocator = Nominatim(user_agent="smart-street")
    location = geolocator.reverse(f"{latitude}, {longitude}")
    road_name = location.address.split(",")[0]
    return road_name

# latitude, longitude = get_current_location()
# print(longitude, latitude)
# road_name = get_road_name()
# print(road_name)
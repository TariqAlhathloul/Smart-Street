import geocoder
import requests
import os
import json
from geopy.geocoders import Nominatim

"""
make a http request to get the current location of the raspberry pi
then convert the response to json and extract the latitude and longitude
"""

def get_current_location():
    """
    No parameters.
    the function will return the [latitude, longitude] of the camera.
    """
    response = requests.get(os.getenv('GEO_KEY'))
    if response.status_code != 200:
        print(f"Error getting location, response code : {response.status_code}")
    data = json.loads(response.content)
    latitude = data['latitude']
    longitude = data['longitude']
    return latitude, longitude

def get_road_name():
    """
    No parameters.
    the function will return the road name of the camera.
    """
    latitude, longitude = get_current_location()
    geolocator = Nominatim(user_agent="smart-street")
    location = geolocator.reverse(f"{latitude}, {longitude}")
    return location.address
# print(get_current_location())

road_name = get_road_name()
print(road_name)
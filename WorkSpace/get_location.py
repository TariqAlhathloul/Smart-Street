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
    response = requests.get(os.getenv('GEO_KEY'))
    if response.status_code != 200:
        raise Exception(f"Error getting location, response code : {response.status_code}")
    data = json.loads(response.content)
    latitude = data['latitude']
    longitude = data['longitude']
    return latitude, longitude

print(get_current_location())
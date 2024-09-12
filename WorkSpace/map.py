import folium
from get_location import get_current_location

"""
display the location of the camera.
returns the map as an html file.
"""
# the get_current_location will return the latitude and longitude of the camera
location = get_current_location()

map = folium.Map(location=location, zoom_start=15)

folium.CircleMarker(location, radius=10, color='red').add_to(map)

folium.Marker(location).add_to(map)

map.save('map.html')
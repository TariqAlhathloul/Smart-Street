import folium
from get_location import current_location

"""
display the location of the camera.
returns the map as an html file.
"""

location = current_location() # returns latitude and longitude

map = folium.Map(location=location, zoom_start=15)

folium.CircleMarker(location, radius=10, color='red').add_to(map)

folium.Marker(location).add_to(map)

map.save('map.html')
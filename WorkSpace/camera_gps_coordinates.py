import serial
import pynmea2
from geopy.geocoders import Nominatim
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chatbot.Audio import Audio

def get_current_location():
    """
    This function returns the [latitude, longitude] of the camera.
    It reads GPS data from the serial port and extracts the location.
    """
    #set serial port
    port = "/dev/ttyAMA0"
    ser = serial.Serial(port, baudrate=9600, timeout=0.5)
    
    while True:
        try:
            #read data from the serial port
            newdata = ser.readline().decode('ascii', errors='replace').strip()

            #check if the data starts with "$GPRMC" (RMC NMEA sentence)
            if newdata[0:6] == "$GPRMC":
                newmsg = pynmea2.parse(newdata)
                
                # Only return valid GPS data
                if newmsg.status == 'A':
                    lat = newmsg.latitude
                    lng = newmsg.longitude
                    return lat, lng
                else:
                    print("NO GPS DATA")
                    return None, None

        except serial.SerialException as e:
            print(f"Serial error: {e}")
            return None, None
        except pynmea2.ParseError as e:
            print(f"NMEA Parse error: {e}")
            return None, None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None, None

def get_road_name():
    """
    This function returns the road name of the camera.
    It reverse geocodes the GPS coordinates to obtain the road name.
    """
    latitude, longitude = get_current_location()

    if latitude is not None and longitude is not None:
        try:
            # reverse geocoding to get road name
            geolocator = Nominatim(user_agent="smart-street")
            location = geolocator.reverse(f"{latitude}, {longitude}")
            
            if location is not None:
                road_name = location.address.split(",")[0]
                return road_name
            else:
                return None

        except Exception as e:
            print(f"Error in reverse geocoding: {e}")
            return None
    else:
        print("Invalid GPS coordinates.")
        return None


Au = Audio()
latitude, longitude = get_current_location()
print(f"Latitude: {latitude}, Longitude: {longitude}")
road_name = get_road_name()
Au.printAr(road_name)
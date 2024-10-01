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
    # Set up serial port
    port = "/dev/ttyAMA0"
    ser = serial.Serial(port, baudrate=9600, timeout=0.5)
    
    while True:
        try:
            # Read a line of data from the serial port
            newdata = ser.readline().decode('ascii', errors='replace').strip()

            # Check if the data starts with "$GPRMC" (RMC NMEA sentence)
            if newdata[0:6] == "$GPRMC":
                newmsg = pynmea2.parse(newdata)
                
                # Only return valid GPS data (status 'A' means valid)
                if newmsg.status == 'A':
                    lat = newmsg.latitude
                    lng = newmsg.longitude
                    print(f"Latitude: {lat}, Longitude: {lng}")
                    return lat, lng
                else:
                    print("Waiting for valid GPS data...")

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
            # Reverse geocoding to get road name
            geolocator = Nominatim(user_agent="smart-street")
            location = geolocator.reverse(f"{latitude}, {longitude}")
            
            if location is not None:
                road_name = location.address.split(",")[0]
                print(f"Road Name: {road_name}")
                return road_name
            else:
                print("Could not find a location for the given coordinates.")
                return None

        except Exception as e:
            print(f"Error in reverse geocoding: {e}")
            return None
    else:
        print("Invalid GPS coordinates.")
        return None

# Example usage
Au = Audio()
road_name = get_road_name()
Au.printAr(road_name)

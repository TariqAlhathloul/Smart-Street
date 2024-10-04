import serial
import pynmea2
import time


"""
the port connected to GPS module is /dev/ttyAMA0
command ls -l /dev, and look for serial0 and serial1 ports
lrwxrwxrwx 1 root root           8 Oct  2 05:16 serial0 -> ttyAMA10
lrwxrwxrwx 1 root root           5 Oct  2 05:16 serial1 -> ttyS0
"""

# connect to the serial port
port = "/dev/ttyAMA10"
ser = serial.Serial(port, baudrate=9600, timeout=0.5)
newdata = ser.readline().decode('ascii', errors='replace').strip()

while True:
    try:
        # read a line of data from the serial port
        newdata = ser.readline().decode('ascii', errors='replace').strip()

        # check if the data starts with "$GPRMC" (RMC NMEA sentence)
        if newdata[0:6] == "$GPRMC":
            newmsg = pynmea2.parse(newdata)
            lat = newmsg.latitude
            lng = newmsg.longitude
            gps = f"Latitude={lat}, Longitude={lng}"
            print(gps)

    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except pynmea2.ParseError as e:
        print(f"NMEA Parse error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    #sleep for 5sec before reading again
    time.sleep(1)

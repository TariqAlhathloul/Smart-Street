

"""

"""

import csv
import datetime as dt
from get_location import get_current_location

date = dt.datetime.now().date()
time = dt.datetime.now().time().strftime('%H:%M:%S')
violation_type = 'over taking from left'
street_name = 'طريق ابو بكر الصديق شمال'
license_plate_number = 'HDR 5803'
vehicle_type = 'car'
longitude, latitude = get_current_location()

date, time, license_plate_number, street_name, violation_type, vehicle_type
with open('../Data/detections/Violations_detected.csv', mode='a') as file:
    writer = csv.writer(file)
    writer.writerow([date, time, license_plate_number,street_name, violation_type, vehicle_type])

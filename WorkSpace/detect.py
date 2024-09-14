

"""
run a real time detection of violations and save the detections in a csv file
1- date of the voilation
2- time of the voilation
3- license plate number
4- street name
5- longitude, latitude
6- violation type
7- viehicle type
"""

import csv
import cv2
import datetime as dt 
from get_location import get_current_location, get_road_name
from ultralytics import YOLO
import torch
torch.cuda.is_available()
model = YOLO('../Models/best.onnx', task='segment')

date = dt.datetime.now().date()
time = dt.datetime.now().time().strftime('%H:%M:%S')
violation_type = 'over taking from right'
#road_name, zip_code = get_road_name()
license_plate_number = 'HDR 5803'
vehicle_type = 'car'
longitude, latitude = get_current_location()

model.predict(source='0')
with open('../Data/Violations_detected.csv', mode='a') as file:
    writer = csv.writer(file)
    writer.writerow([date, time, license_plate_number, 
    violation_type, vehicle_type, longitude, latitude, road_name, zip_code])

"""
the script detects vehicles that are overtaking in non-permitted areas and saves the violation information to a csv file
"""
import numpy as np
import cv2
from ultralytics import YOLO
import datetime as dt
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from WorkSpace.get_location import get_current_location, get_road_name
from WorkSpace.OCR import OCR


def calculate_center(bbox):
    """
    the function takes a bbox tensor and 
    calculates the center of the bbox
    """
    #convert to numpy
    x1, y1, x2, y2 = bbox[0].numpy()

    #calculate x,y centers
    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)

    return (center_x, center_y)

def draw_bbox(image, bbox, color=(0, 0, 255), thickness=2):
    """
    the function draws a bounding box on an image
    """
    pt1 = bbox.xywh[0][0:2].numpy()
    pt2 = bbox.xywh[0][2:4].numpy()

    top_left = (int(pt1[0] - pt2[0] / 2), int(pt1[1] - pt2[1] / 2))
    bottom_right = (int(pt1[0] + pt2[0] / 2), int(pt1[1] + pt2[1] / 2))

    bbox = cv2.rectangle(image, top_left, bottom_right, color, thickness)
    return bbox

def is_overtaking(vehicle_center, line_center):
    """
    the function checks if a vehicle is overtaking in non-permitted areas
    """
    return vehicle_center[0] > line_center[0]

#load the model
model = YOLO('../Models/best.onnx', task='segment')

#start video capture
cap = cv2.VideoCapture('../Data/example_video.MP4')
assert cap.isOpened(), 'Cannot capture video'

#video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

#video writer
output_path = '../Data/output_video.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#violation information
latitude, longitude = get_current_location()
street_name = get_road_name()
violation_type = 'overtaking'
date = dt.datetime.now().strftime('%Y-%m-%d')
license_plate_number = None
counter = 0

# initial center points
line_center = (1, 1)
vehicle_center = (1, 1)

while cap.isOpened():
    #start reading framess
    success, frame = cap.read()
    if not success:
        break

    #send frames to the model
    results = model(frame, conf=0.3)

    #start timer and wirte it to the frames
    current_time = dt.datetime.now()
    cv2.putText(frame, current_time.strftime('%Y-%m-%d %H:%M:%S'), (20, 1850), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)

        #detect the solid-yellow line and thier center
    for mask, box in zip(results[0].masks.xy, results[0].boxes):
        #  solid yellow lines detected
        if box.cls[0].item() == 3: 
            line_center = calculate_center(box.xyxy)

        # vehicle detected
        else:
            vehicle_center = calculate_center(box.xyxy)
            #check if the vehicle is overtaking
            if is_overtaking(vehicle_center, line_center):
                cv2.putText(frame, "Violation Detected !", (20, 650), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                #draw the bounding box on violated vehicle
                frame = draw_bbox(frame, box, color=(0, 0, 255), thickness=10)
                #crop detected violation image and save it
                x1, y1, x2, y2 = box.xyxy[0]
                cv2.imwrite(f'../Data/violations_images/violation{counter}.jpg', frame[int(y1):int(y2), int(x1):int(x2)])
                counter += 1
                #get vehicle type
                vehicle_type = ['bus', 'car', 'truck'][int(box.cls[0].item())]
                # append the violation data to the dataframe
                with open('../Data/violations.csv', 'a') as file:
                    file.write(f'{date},{license_plate_number}, {vehicle_type}, {violation_type}, {longitude}, {latitude}, {street_name}\n')
    out.write(frame)

cap.release()
out.release()
# TODO: apply OCR on the saved image to get the license plate number and append it to the violations.csv file
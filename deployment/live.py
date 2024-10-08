import os
import sys
from ultralytics import YOLO
import datetime as dt
import cv2
import numpy as np
import streamlit as st
#append the path to the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from WorkSpace.camera_gps_coordinates import get_current_location, get_road_name
from WorkSpace.OCR import read_license_plate
from WorkSpace.Detection import Detect
from WorkSpace.insert_data import insert_data
import pytz

#set the Riyadh timezone
riyadh_tz = pytz.timezone('Asia/Riyadh')

# create a directory to save the violation images
os.makedirs('../resources/violation_images', exist_ok=True)

# initialize instance from the Detect class
detect = Detect()

date = dt.datetime.now().strftime('%Y-%m-%d')
start = dt.datetime.now()

# load model
model = YOLO('../Models/Bestmodel.onnx', task='segment')

#start video capture form the camera
cap = cv2.VideoCapture(0)
assert cap.isOpened(), 'Cannot capture video'

#video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
print(f"width: {width}, height: {height}, fps: {fps}")

#video writer
output_path = f'../resources/VIDEO at {dt.datetime.now().strftime("%Y-%m-%d %H_%M")}.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))

#counter to index saved images
counter = 0

# initial values for center points
line_center = (1, 1)
vehicle_center = (1, 1)

#placeholder for the frame
frame_placeholder = st.empty()

#initial value for license plate number
license_plate_number = None

while cap.isOpened():

    #start capturing from the camera
    success, frame = cap.read()

    #end of capturing
    if not success:
        break

    #write the current time and date on the bottom left of the frame
    current_time = dt.datetime.now(riyadh_tz)
    text = current_time.strftime('%Y-%m-%d %H:%M:%S')
    cv2.putText(frame, text, (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, "violation detected !", (5, int(height/6)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)


    #send frames to the model
    results = model(frame, conf=0.2, imgsz=640)

    try:
        for box, mask in zip(results[0].boxes, results[0].masks.xy):

            # class 2 solid-yellow-line detected
            if int(box.cls.item()) == 2:
                #get the center of the solid-yellow-line
                line_center = detect.get_center(box.xyxy)
                #fill the mask points with yellow color
                mask_points = np.int32([mask])
                cv2.fillPoly(frame, mask_points, color=(0, 255, 255))

            # class 0 car detected
            elif int(box.cls.item()) == 1:
                #get the center of the vehicle
                vehicle_center = detect.get_center(box.xyxy)
                is_violating, violation_type = detect.is_overtaking(vehicle_center, line_center, width)
                
                #check if the vehicle is overtaking
                if is_violating and line_center != (1, 1):
                    #draw red bounding box on the violating vehicle
                    detect.draw_bbox(frame, box, color=(0, 0, 255))
                    #write the violation detected text on the top left of the frame
                    cv2.putText(frame, "violation detected !", (20, int(height/2)), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                    #crop and save the image of violating vehicle and save it
                    x1, y1, x2, y2 = box.xyxy[0]
                    cv2.imwrite(f'../resources/violation_images/violation{counter}.jpg', frame[int(y1):int(y2), int(x1):int(x2)])
                    counter += 1
                    #play a beep sound when a violation is detected
                    detect.play_sound('../resources/beep-sound-8333.mp3')

                    #class 1 license plate detected
                    if int(box.cls.item()) == 0:
                        # send the cropped image to the ocr model
                        x1m, y1m, x2x, y2x = box.xyxy[0]
                        cv2.imwrite(f'../resources/cropped_plate_images/plate{counter}.jpg', frame[int(y1):int(y2), int(x1):int(x2)])
                        license_plate_number = read_license_plate(frame[int(y1m):int(y2x), int(x1m):int(x2x)], counter)
                        detect.draw_bbox(frame, box, color=(0, 255, 0), thickness=2)
                        #get the vehicle type
                        #vehicle_type = ['bus', 'license_plate','car', 'solid-yellow-line', 'truck'][int(box.cls[0].item())]
                        #I commented the above line of code 'vehicle_type' because we have only 'car' class in the new model
                        
                        #violation geolocation information
                        latitude, longitude = get_current_location()
                        street_name = get_road_name()

                        if license_plate_number != None:
                            #after having all the information, save it to the database
                            insert_data(date, current_time.strftime('%H:%M:%S'), license_plate_number, "car", violation_type, latitude, longitude, street_name)
        
    except AttributeError as e:
        #this exception is raised when the model does not detect any object
        pass
    except KeyboardInterrupt as e:
        break
    
    frame_placeholder.image(frame, channels="BGR", caption="Smart Street")
    
    out.write(frame)

#release the camera capture and video writer
cap.release()
out.release()
print(f"Time elapsed: {dt.datetime.now() - start}")
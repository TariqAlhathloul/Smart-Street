import os
import sys
from ultralytics import YOLO
import datetime as dt
import cv2
import streamlit as st
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from WorkSpace.camera_gps_coordinates import get_current_location, get_road_name
from WorkSpace.OCR import read_license_plate
from WorkSpace.Detection import Detect
from WorkSpace.insert_data import insert_data

os.makedirs('../resources/violation_images', exist_ok=True)

detect = Detect()

# camera information
# latitude, longitude = get_current_location()
# street_name = get_road_name()
latitude, longitude = " ", " "
street_name = ""
date = dt.datetime.now().strftime('%Y-%m-%d')

# load model
model = YOLO('../Models/best(1).onnx', task='segment')

#start video capture
cap = cv2.VideoCapture(0)
assert cap.isOpened(), 'Cannot capture video'

#video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
print(f"width: {width}, height: {height}, fps: {fps}")


#video writer
output_path = '../resources/OUTPUT(1).mp4'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(output_path, fourcc, 15, (width, height))


#counter to index saved images
counter = 0

# initial center points
line_center = (1, 1)
vehicle_center = (1, 1)

#placeholder for the frame
frame_placeholder = st.empty()

while cap.isOpened():

    success, frame = cap.read()

    if not success:
        break

    #write the current time and date on the frames
    current_time = dt.datetime.now()
    cv2.putText(frame, current_time.strftime('%Y-%m-%d %H:%M:%S'), (20, 1850), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)

    #send frames to the model
    results = model(frame, conf=0.4, imgsz=640)

    for box in results[0].boxes:
        # solid-yellow-line detected
        if int(box.cls.item()) == 2:
            line_center = detect.get_center(box.xyxy)
            cv2.circle(frame, line_center, 10, (0, 0, 255), -1)
            #print("line center ", line_center)

        # vehicle detected
        elif int(box.cls.item()) == 0:
            vehicle_center = detect.get_center(box.xyxy)
            is_violating, violation_type = detect.is_overtaking(vehicle_center, line_center)
            print("vehicle center ", vehicle_center)
            print("line center ", line_center, is_violating)
            cv2.circle(frame, vehicle_center, 10, (0, 255, 0), -1)
            cv2.putText(frame, "violation detected !", (20, 650), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
            

            if is_violating:
                #draw red bounding box on the violating vehicle
                frame = detect.draw_bbox(frame, box, color=(0, 0, 255), thickness=5)
                #put text
                cv2.putText(frame, "violation detected !", (20, 650), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                #crop and save the image of violating vehicle
                x1, y1, x2, y2 = box.xyxy[0]
                cv2.imwrite(f'../resources/violation_images/violation{counter}.jpg', frame[int(y1):int(y2), int(x1):int(x2)])
                counter += 1
                #detect.play_sound(sound)

                #license plate detected
                if int(box.cls.item()) == 1:
                    # send the cropped image to the ocr model
                    license_plate_number = read_license_plate(frame[int(y1)-10:int(y2), int(x1)-10:int(x2)], counter)  
                    #get the vehicle type
                    vehicle_type = ['bus', 'license_plate','car', 'solid-yellow-line', 'truck'][int(box.cls[0].item())]                    
                    #after having all the information, save it to the database
                    if license_plate_number != None:
                        print("violation detected !")
                        insert_data(date, current_time.strftime('%H:%M:%S'), license_plate_number, vehicle_type, violation_type, latitude, longitude, street_name)
    #cv2.imshow('frame', frame)
    frame_placeholder.image(frame, channels="BGR")
    
    out.write(frame)


cap.release()
out.release()
import os
import sys
from ultralytics import YOLO
import datetime as dt
import cv2
import numpy as np
#append the path to the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from WorkSpace.camera_gps_coordinates import get_current_location, get_road_name
from WorkSpace.OCR import read_license_plate
from WorkSpace.Detection import Detect
from WorkSpace.insert_data import insert_data

# create a directory to save the violation images
os.makedirs('../resources/violation_images', exist_ok=True)

# initialize instance from the Detect class
detect = Detect()

# camera geolocation information
latitude, longitude = get_current_location()
street_name = get_road_name()

#get current date to display on the screen
date = dt.datetime.now().strftime('%Y-%m-%d')
start = dt.datetime.now()

# load model
model = YOLO('../Models/best(1).onnx', task='segment')

#start video capture
cap = cv2.VideoCapture('../resources/left-cross-4.MP4')
assert cap.isOpened(), 'Cannot capture video'

#video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
print(f"width: {width}, height: {height}, fps: {fps}")

# we set the frame width and height to fixed values 640 and 480, to have a better processing speed
cap.set(cv2.CAP_PROP_FPS, 20.0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


#video writer
output_path = f'../resources/OUTPUT_VIDEO{dt.datetime.now().strftime("%Y-%m-%d__%H_%M")}.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#counter to index saved images
counter = 0

# initial values for center points
line_center = (1, 1)
vehicle_center = (1, 1)

#initial value for license plate number
license_plate_number = None

while cap.isOpened():

    #start capturing frames from video
    success, frame = cap.read()

    #end of the video
    if not success:
        break
    #resize the frame to 640x480 to have a better processing speed
    #cv2.resize(frame, (640, 480))

    #write the current time and date on the frames
    current_time = dt.datetime.now()
    cv2.putText(frame, current_time.strftime('%Y-%m-%d %H:%M:%S'), (20, 1850), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)

    #send frames to the model
    results = model(frame, conf=0.3, imgsz=640)

    for box, mask in zip(results[0].boxes, results[0].masks.xy):

        # class 2 solid-yellow-line detected
        if int(box.cls.item()) == 2:
            #get the center of the line
            line_center = detect.get_center(box.xyxy)
            #fill the mask points with yellow color
            mask_points = np.int32([mask])
            cv2.fillPoly(frame, mask_points, color=(0, 255, 255))

        # class 0 vehicle detected
        elif int(box.cls.item()) == 0:
            #get the center of the vehicle
            vehicle_center = detect.get_center(box.xyxy)
            is_violating, violation_type = detect.is_overtaking(vehicle_center, line_center, width)
            #draw a green circle on the vehicle center
            cv2.circle(frame, vehicle_center, 10, (0, 255, 0), -1)

            #check if the vehicle is overtaking
            if is_violating and line_center != (1, 1):
                #draw red bounding box on the violating vehicle
                detect.draw_bbox(frame, box, color=(0, 0, 255), thickness=5)
                #draw a red circle on the violating vehicle center
                cv2.circle(frame, vehicle_center, 10, (0, 0, 255), -1)
                #write the violation detected text on the top left of the frame
                cv2.putText(frame, "violation detected !", (20, int(height/2)), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

                #crop and save the image of violating vehicle
                x1, y1, x2, y2 = box.xyxy[0]
                cv2.imwrite(f'../resources/violation_images/violation{counter}.jpg', frame[int(y1):int(y2), int(x1):int(x2)])
                counter += 1

                #license plate detected
                if int(box.cls.item()) == 1:
                    # send the cropped image to the ocr model
                    license_plate_number = read_license_plate(frame[int(y1)-10:int(y2), int(x1)-10:int(x2)], counter)              
                    #after having all the information, save it to the database
                    if license_plate_number != None:
                        print("violation detected !")
                        insert_data(date, current_time.strftime('%H:%M:%S'), license_plate_number, "car", violation_type, latitude, longitude, street_name)
    out.write(frame)


#release the video capture and writer
cap.release()
out.release()
print(f"Time elapsed: {dt.datetime.now() - start}")
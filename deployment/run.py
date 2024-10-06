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
# load the model
model = YOLO('../Models/best(1).onnx', task='segment')

#start video capture from the camera
cap = cv2.VideoCapture(0)
assert cap.isOpened(), 'Cannot capture video'

#video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
print(f"width: {width}, height: {height}, fps: {fps}")


#video writer
output_path = f'../resources/OUTPUT_LIVE_VIDEO{dt.datetime.now().strftime("%Y-%m-%d %H_%M")}.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID') 
out = cv2.VideoWriter(output_path, fourcc, fps, (640, 480))
license_plate_number = None

#counter to index saved violation images
counter = 0

# initial values for center points
line_center = (1, 1)
vehicle_center = (1, 1)

while cap.isOpened():

    #start capturing frames from camera
    success, frame = cap.read()

    #end of the capturing
    if not success:
        break

    #write the current time and date on the bottom left of the frame
    current_time = dt.datetime.now()
    text = current_time.strftime('%Y-%m-%d %H:%M:%S')
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 5)[0]

    #send frames to the model
    results = model(frame, conf=0.4, imgsz=640)


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
            elif int(box.cls.item()) == 0:
                #get the center of the vehicle
                vehicle_center = detect.get_center(box.xyxy)
                is_violating, violation_type = detect.is_overtaking(vehicle_center, line_center)
                #draw a circle on the vehicle center
                cv2.circle(frame, vehicle_center, 10, (0, 255, 0), -1)            

                #check if the vehicle is overtaking
                if is_violating and line_center != (1, 1):
                    #draw red bounding box on the violating vehicle
                    detect.draw_bbox(frame, box, color=(0, 0, 255), thickness=5)
                    #crop and save the image of violating vehicle and save it
                    x1, y1, x2, y2 = box.xyxy[0]
                    cv2.imwrite(f'../resources/violation_images/violation{counter}.jpg', frame[int(y1):int(y2), int(x1):int(x2)])
                    counter += 1
                    #detect.play_sound(sound)

                    # write the violation detected text on the top left of the frame
                    cv2.putText(frame, "violation detected !",(20, int(height/2)), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

                    #class 1 license plate detected
                    if int(box.cls.item()) == 1:
                        # send the cropped image to the ocr model
                        license_plate_number = read_license_plate(frame[int(y1)-10:int(y2), int(x1)-10:int(x2)], counter)
                        #get the vehicle type
                        vehicle_type = ['bus', 'license_plate','car', 'solid-yellow-line', 'truck'][int(box.cls[0].item())]                    
                        #after having all the information, save it to the database
                        if license_plate_number != None:
                            insert_data(date, current_time.strftime('%H:%M:%S'), license_plate_number, vehicle_type, violation_type, latitude, longitude, street_name)
    except AttributeError as e:
        print(e)
        pass
    out.write(frame)


#release the camera capture and video writer
cap.release()
out.release()
print(f"Time elapsed: {dt.datetime.now() - start}")
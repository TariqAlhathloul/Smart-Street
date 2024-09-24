from ultralytics import YOLO
import datetime as dt
import cv2
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from WorkSpace.get_location import get_current_location, get_road_name
from WorkSpace.OCR import read_license_plate
from WorkSpace.Detecation import Detecation

detect = Detecation()

# camera information
latitude, longitude = get_current_location()
street_name = get_road_name()
date = dt.datetime.now().strftime('%Y-%m-%d')

# load model

model = YOLO('../Models/best.onnx', task='segment')

#start video capture
cap = cv2.VideoCapture('../resources/example_video.MP4')
assert cap.isOpened(), 'Cannot capture video'

#video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
print(f"width: {width}, height: {height}, fps: {fps}")

#video writer
output_path = '../resources/outPut(5).mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))


#counter to index saved images
counter = 0

# initial center points
line_center = (1, 1)
vehicle_center = (1, 1)

#{0: 'bus', 1: 'car', 2: 'license_plate', 3: 'solid-yellow-line', 4: 'truck'}
vehicles = [0, 1, 2, 4]

while cap.isOpened():

    success, frame = cap.read()

    if not success:
        break

    #write the current time and date on the frames
    current_time = dt.datetime.now()
    cv2.putText(frame, current_time.strftime('%Y-%m-%d %H:%M:%S'), (20, 1850), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)

    #send frames to the model
    results = model(frame, conf=0.3)

    for box in results[0].boxes:

        # solid-yellow-line detected
        print(box.cls)
        print(box.xyxy)
        if 3 in box.cls:
            line_center = detect.calculate_center(box.xyxy)

        # vehicle detected
        elif box.cls in vehicles:
            vehicle_center = detect.calculate_center(box.xyxy)

            is_violating, violation_type = detect.is_overtaking(vehicle_center, line_center)

            if is_violating:
                #draw red bounding box on the violating vehicle
                frame = detect.draw_bbox(frame, box, color=(0, 0, 255), thickness=10)
                #put text
                cv2.putText(frame, "violation detected !", (20, 650), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                #crop and save the image of violating vehicle
                x1, y1, x2, y2 = box.xyxy[0]
                cv2.imwrite(f'../resources/violations_images/violation{counter}.jpg', frame[int(y1):int(y2), int(x1):int(x2)])
                counter += 1

                #license plate detected
                if 2 in box.cls:
                    # send the cropped image to the ocr model
                    license_plate_number = read_license_plate(frame[int(y1):int(y2), int(x1):int(x2)], counter)
                    #get the vehicle type
                    vehicle_type = ['bus', 'license_plate','car', 'solid-yellow-line', 'truck'][int(box.cls[0].item())]                    #after have all the information, save it to the database
                    try:
                        with open('../Database/violations_detected.csv', 'a') as file:
                            file.write(f"{date},{current_time.strftime('%H:%M:%S')},{license_plate_number},{vehicle_type},{violation_type},{latitude},{longitude},{street_name}\n")
                    except Exception as e:
                        print(f"Error: {e}")
    out.write(frame)


cap.release()
out.release()
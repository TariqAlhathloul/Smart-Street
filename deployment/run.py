"""
the script detects vehicles that are overtaking in non-permitted areas,
and saves the violation information to a csv file.
"""
import cv2
from ultralytics import YOLO
import datetime as dt
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from WorkSpace.get_location import get_current_location, get_road_name
from WorkSpace.OCR import read_license_plate


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
    we will use it to draw bbox only on the violated cars
    """
    #convert to numpy
    pt1 = bbox.xywh[0][0:2].numpy()
    pt2 = bbox.xywh[0][2:4].numpy()
    #calculate top left and bottom right points
    top_left = (int(pt1[0] - pt2[0] / 2), int(pt1[1] - pt2[1] / 2))
    bottom_right = (int(pt1[0] + pt2[0] / 2), int(pt1[1] + pt2[1] / 2))
    #draw the bounding box
    bbox = cv2.rectangle(image, top_left, bottom_right, color, thickness)
    return bbox

def is_overtaking(vehicle_center, line_center):
    """
    the function checks if a vehicle is overtaking in non-permitted areas
    """
    if line_center[0] > 1250:
        #meaning that the line is on the right side
        distance = vehicle_center[0] - line_center[0]
        # distance threshold
        is_overtaking = distance > 120 and vehicle_center[0] > line_center[0] and distance < 800
    else:
        #meaning that the line is on the left side
        distance = line_center[0] - vehicle_center[0]
        # distance threshold
        is_overtaking = vehicle_center[0] < line_center[0]
    return is_overtaking

#load the model
model = YOLO('./Models/best.onnx', task='segment')

#start video capture
cap = cv2.VideoCapture(0)
assert cap.isOpened(), 'Cannot capture video'

#video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
print(f"width: {width}, height: {height}, fps: {fps}")

#video writer
output_path = './resources/outPut(2).mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

#violation information
latitude, longitude = get_current_location()
street_name = get_road_name()
violation_type = 'overtaking'
date = dt.datetime.now().strftime('%Y-%m-%d')
license_plate_number = None

#counter to index saved images
counter = 0
#skip frames for faster processing
skip_frames = 5

# initial center points
line_center = (1, 1)
vehicle_center = (1, 1)

#{0: 'bus', 1: 'car', 2: 'license_plate', 3: 'solid-yellow-line', 4: 'truck'}
vehicles = [0, 1, 2, 4]

#start capturing frames
while cap.isOpened():

    success, frame = cap.read()
    if not success:
        break

    #skip frames for faster processing
    #current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
    #if current_frame % skip_frames != 0:
        #continue
    #send frames to the model
    results = model(frame, conf=0.3)

    #start timer and wirte it to the frames
    current_time = dt.datetime.now()
    cv2.putText(frame, current_time.strftime('%Y-%m-%d %H:%M:%S'), (20, 1850), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
    
    #loop over the detected masks and boxes
    for box in results[0].boxes:
        #solid-yellow-line detected
        if 3 in box.cls: 
            line_center = calculate_center(box.xyxy)
            #cv2.circle(frame, line_center, 15, (0, 0, 255), -1)

        # vehicle detected
        elif box.cls in vehicles:
            vehicle_center = calculate_center(box.xyxy)
            overtaking = is_overtaking(vehicle_center, line_center)

            #vehicle is overtaking and solid-yellow-line is detected
            if overtaking and line_center != (1, 1): 
                cv2.putText(frame, "Violation Detected !", (20, 650), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)
                #draw a circle on the vehicle center
                #cv2.circle(frame, vehicle_center, 15, (255, 0, 0), -1)
                #draw the bounding box on violated vehicle
                frame = draw_bbox(frame, box, color=(0, 0, 255), thickness=10)
                #crop detected violation image and save it
                x1, y1, x2, y2 = box.xyxy[0]
                cv2.imwrite(f'./resources/violations_images/violation{counter}.jpg', frame[int(y1):int(y2), int(x1):int(x2)])
                counter += 1

                #license plate is detected
                if 2 in box.cls:
                    #send croped image to ocr function
                    license_plate_number = read_license_plate(frame[int(y1):int(y2), int(x1):int(x2)], counter)
                    #get vehicle type
                    vehicle_type = ['bus', 'license_plate','car', 'solid-yellow-line', 'truck'][int(box.cls[0].item())]
                    # append the violation data to thataframe
                    with open('./Database/violations_detected.csv', 'a') as file:
                        file.write(f"{date},{current_time.strftime('%H:%M:%S')},{license_plate_number},{vehicle_type},{violation_type},{latitude},{longitude},{street_name}\n")
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    cv2.imshow("Video", frame)
    out.write(frame)

cap.release()
out.release()
cv2.destroyAllWindows()

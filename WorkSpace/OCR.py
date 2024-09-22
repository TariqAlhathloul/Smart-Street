import cv2
from ultralytics import YOLO
import easyocr

"""
apply OCR on the detected violation cars to get the license plate number
"""

# load model
model = YOLO('../Models/ocr.pt')
# initialize the reader
reader = easyocr.Reader(['en'], gpu=False, model_storage_directory='../Models')


def read_license_plate(image, image_counter):
    """
    the function takes an image as input and returns the detected license plate number if detected or None
    """
    #detect license plate
    results = model(image)
    #counter to index saved license plate images
    #check if there is a license plate detected
    if results[0].boxes.xyxy.size(0) == 0:
        return None
    
    #after detection crop the image based on the bbox detected
    x1, y1, x2, y2 = results[0].boxes.xyxy[0]
    crop_img = image[int(y1):int(y2), int(x1):int(x2)]
    cv2.imwrite(f'../resources/violations_plates/plate{image_counter}.jpg', crop_img)

    # now let's process the cropped license plate image to have better results with OCR
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
    
    #Noise reduction
    bfilter = cv2.bilateralFilter(gray, 11, 17, 17) 
    
    # read the license plate
    result = reader.readtext(bfilter)

    # fillter results with confidence > 0.5
    license_plate_number = []
    for detection in result:
        if detection[2] > 0.5:
            license_plate_number.append(detection[1])
        else:
            return None
    
    return ' '.join(license_plate_number)

# image = cv2.imread('../Data/violations_images/violation42.jpg')
# results = read_license_plate(image)
# print(results)
# # real license plate number: HRD 7863
# # output: MT 7862
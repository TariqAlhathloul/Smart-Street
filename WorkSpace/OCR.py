import cv2
import easyocr
import os
import re

"""
apply OCR on the detected violation cars to get the license plate number
"""

#initialize the reader
reader = easyocr.Reader(['en'], gpu=False, model_storage_directory='../Models')

#create a directory to save the violation car license plate images
os.makedirs('../resources/cropped_plate_images/', exist_ok=True)

def read_license_plate(image, image_counter):
    """
    the function takes an image as input and returns the number on the  license plate
    """
    cv2.imwrite(f'../resources/cropped_plate_images/plate{image_counter}.jpg', image)

    # process the cropped license plate image to have better results with OCR
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #noise reduction
    bfilter = cv2.bilateralFilter(gray, 17, 15, 15) 
    
    # read the license plate
    result = reader.readtext(bfilter)

    license_plate_number = []
    for detection in result:
        # fillter results with confidence > 0.2
        if detection[2] > 0.1:
            license_plate_number.append(detection[1])


    # if no license plate were detected
    if not license_plate_number:
        return None
    
    # clean the text from any special characters
    text = re.sub('[^A-Za-z0-9]+', ' ', ''.join(license_plate_number))
    
    return text

# image = cv2.imread('../Database/violations_plates/plate37.jpg')
# results = read_license_plate(image, 1)
# print(results)
import cv2
import easyocr

"""
apply OCR on the detected violation cars to get the license plate number
"""

# initialize the reader
reader = easyocr.Reader(['en'], gpu=False, model_storage_directory='../Models')


def read_license_plate(image, image_counter):
    """
    the function takes an image as input and returns the number on the  license plate
    """
    cv2.imwrite(f'../resources/violations_plates/plate{image_counter}.jpg', image)

    # process the cropped license plate image to have better results with OCR
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    #noise reduction
    bfilter = cv2.bilateralFilter(gray, 11, 17, 17) 
    
    # read the license plate
    result = reader.readtext(bfilter)

    license_plate_number = []
    for detection in result:
        # fillter results with confidence > 0.2
        if detection[2] > 0.2:
            license_plate_number.append(detection[1])



    # if no license plate were detected
    if not license_plate_number:
        return None
    return ' '.join(license_plate_number) 

# image = cv2.imread('../Database/violations_plates/first_model_plate37.jpg')
# results = read_license_plate(image, 1)
# print(results)
# # real license plate number: HRD 7863
# # output: MT 7862
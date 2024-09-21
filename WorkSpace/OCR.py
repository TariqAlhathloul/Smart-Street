import cv2
from ultralytics import YOLO
import easyocr


# load model
model = YOLO('../Models/ocr.pt')

# get the license plate text using easyocr
def OCR(frame):
    """
    the function reads the license plate text from the frame
    """
    results = model(frame)
    # crop the imge within the bbox of the license plate
    x1, y1, x2, y2 = results[0].boxes.xyxy[0]
    cropped_frame = frame[int(y1):int(y2), int(x1):int(x2)]
    reader = easyocr.Reader(['en'], gpu=False, model_storage_directory='../Models')
    gray = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2GRAY)
    noise_flt = cv2.bilateralFilter(gray, 11, 17, 17)
    results = reader.readtext(noise_flt)
    return results

OCR('../Data/violations_images/violation69.jpg')
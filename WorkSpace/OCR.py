import cv2
from ultralytics import YOLO
import easyocr
#import pytesseract
import re


# load model
model = YOLO('../Models/ocr.pt')


def pytesseract_OCR(img):
    # convert to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # fillter noise
    text = pytesseract.image_to_string(gray)
    # clean text from special characters
    text = re.sub(r'[^A-Za-z0-9]+', '', text)
    return text

# get the license plate text using easyocr
def easyOCR(frame):
    reader = easyocr.Reader(['en'])
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    noise_flt = cv2.bilateralFilter(gray, 11, 17, 17)
    results = reader.readtext(noise_flt)
    return results

image = cv2.imread('Data/plate.jpg')
results = model(image)

# crop the imge within the bbox
x1, y1, x2, y2 = results[0].boxes.xyxy
cropped_img = image[int(y1):int(y2), int(x1):int(x2)]
# save cropped image
cv2.imwrite('./cropped_plate.jpg', cropped_img)
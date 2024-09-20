import streamlit as st
import numpy as np
import cv2
from ultralytics import YOLO
from PIL import Image
import easyocr
import io
import pytesseract
import re
# load model
model = YOLO('../License-Plate-Detection-and-Recognition/BestModel1/weights/best.pt')

# title of the app
st.title("License Plate Detection")
st.write("Upload an image to detect license plate.")
language = st.radio("Choose the license plate language:", ('English', 'Arabic'))

# function to convert 
def convet_to_opencv_image(image):
    image = Image.open(image)
    image_np = np.array(image)
    image_cv2 = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    return image_cv2

def ocr(img):
    # convert to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # fillter noise
    text = pytesseract.image_to_string(gray)
    # clean text from special characters
    text = re.sub(r'[^A-Za-z0-9]+', '', text)
    return text

# get the license plate text using easyocr
def get_license_plate(frame):
    reader = easyocr.Reader(['ar'])
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    noise_flt = cv2.bilateralFilter(gray, 11, 17, 17)
    results = reader.readtext(noise_flt)
    return results

# convert the image to PIL image then to bytes
def convert_to_downloadable(image):
    pil_image = Image.fromarray(image)
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    return byte_im

# file uploader
image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if image is not None:

    # convert to open cv image
    image = convet_to_opencv_image(image)
  
    # send the image to the model
    results = model(image)
    # draw bbox on the image
    #annotated_image = results[0].plot()
    
    # check if any boxes were detected
    if len(results[0].boxes.xyxy) > 0:
        boxes = results[0].boxes.xyxy.tolist()

        # draw the bbox
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 1)

        #crop the license plate from the image
        x1, y1, x2, y2 = boxes[0]
        cropped_img = image[int(y1):int(y2), int(x1):int(x2)]

        if language == 'English':
            text = ocr(cropped_img)
        else:  # arabic selected
            text = get_license_plate(cropped_img)
            text = text[0][-2] + text[1][-2]
            text = re.sub(r'[^A-Za-z0-9]+', '', text)


    # convert back to RGB
    annotated_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    if text:
        cv2.putText(annotated_image, text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        st.markdown(
    f"""
    <p style='color: blue; padding: 5px; border-radius: 5px;'>
    Detected License Plate Number: {text}
    </p>
    """,
    unsafe_allow_html=True)

    # display the image
    st.image(annotated_image, caption='Detected License Plate', use_column_width=True)

    # download the image
    annotated_image = convert_to_downloadable(annotated_image)
    st.download_button(label='Download Annotated Image',
                       data=annotated_image,
                       file_name='annotated_image.png',
                       mime='image/png')
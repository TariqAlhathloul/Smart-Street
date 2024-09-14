import cv2


def list_available_cameras(max_index=10):
    available_cameras = []
    for index in range(max_index):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"Camera {index} is available.")
            available_cameras.append(index)
            cap.release()  
        else:
            print(f"Camera {index} is not available.")
    return available_cameras

cameras = list_available_cameras()
print(f"Available cameras: {cameras}")

cap = cv2.VideoCapture(1) 

if not cap.isOpened():
    print("Error: Could not open video device")
    exit()

ret, frame = cap.read()
if ret:
    cv2.imwrite('C:/Users/tariq/Shared/test.jpg', frame)
else:
    print("Error: Couldn't capture a frame")

cap.release()

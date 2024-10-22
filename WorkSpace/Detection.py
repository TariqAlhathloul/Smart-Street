import cv2
import torch
import os
import sys
import numpy as np
#append the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from chatbot.Audio import Audio

class Detect(Audio):
    
    def get_center(self, bbox: torch.Tensor):
        """
        the function takes a bounding box tensor and
        returns the center of the bounding box
        """
        #convert to numpy
        x1, y1, x2, y2 = bbox[0].numpy()
        #calculate x,y centers
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        return (center_x, center_y)
    
    def draw_bbox(self, frame: np.ndarray, bbox: torch.Tensor, color=(0, 0, 255), thickness: int =2):
        """
        the function draws a bounding box on an image
        we will use it to draw bounding boxes only on the violated cars
        """
        #convert to numpy
        pt1 = bbox.xywh[0][0:2].numpy()
        pt2 = bbox.xywh[0][2:4].numpy()
        #calculate top left and bottom right points
        top_left = (int(pt1[0] - pt2[0] / 2), int(pt1[1] - pt2[1] / 2))
        bottom_right = (int(pt1[0] + pt2[0] / 2), int(pt1[1] + pt2[1] / 2))
        #draw the bounding box
        cv2.rectangle(frame, top_left, bottom_right, color, thickness)
        return frame

    def is_overtaking(self, vehicle_center: tuple, line_center: tuple, width=640):
        """
        the function takes a tuple of 'veicle' and 'solid-line' centers
        and checks if the vehicle is overtaking in non-permitted areas
        return True if the vehicle is overtaking, False otherwise
        """
        #we will set the threshold to be the half of the width
        threshold = int(width / 2)
        violation_type = ''
        is_overtaking = False
        #first get the line center position based on the x-axis
        if line_center[0] > threshold and vehicle_center[0] > line_center[0] - 65:
            #meaning that the line is on the right side
            is_overtaking = True
            violation_type = 'overtaking from the right'
        elif line_center[0] < threshold and vehicle_center[0] < line_center[0] + 65:
            #meaning that the line is on the left side
            # distance threshold
            is_overtaking = True
            violation_type = 'overtaking from the left'
        else:
            is_overtaking = False

        return is_overtaking, violation_type

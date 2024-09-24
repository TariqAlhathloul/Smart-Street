import cv2
import torch

class Detecation:

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
    
    def draw_bbox(self, frame, bbox, color=(0, 0, 255), thickness=2):
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
        bbox = cv2.rectangle(frame, top_left, bottom_right, color, thickness)
        return bbox
    
    def is_overtaking(self, veicle_center, line_center):
        """
        the function takes a tuple of 'veicle' and 'solid-line' center
        and checks if the vehicle is overtaking in non-permitted areas
        return True if the vehicle is overtaking, False otherwise
        """
        violation_type = ''
        is_overtaking = False
        #first get the line center position based on the x-axis
        if line_center[0] > 1250:
            #meaning that the line is on the right side
            distance = veicle_center[0] - line_center[0]
            # distance threshold
            is_overtaking = distance > 120 and veicle_center[0] > line_center[0] and distance < 800
            violation_type = 'overtaking from the right'
        else:
            #meaning that the line is on the left side
            distance = line_center[0] - veicle_center[0]
            # distance threshold
            is_overtaking = veicle_center[0] < line_center[0]
            violation_type = 'overtaking from the left'

        return is_overtaking, violation_type

import yolov5
import cv2
import numpy as np
import os

global cType
from CameraType import CameraType
cType = CameraType()

def find_ball(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    model_name = 'Yolov5_models'
    yolov5_model = 'balls5n.pt'
    model_labels = 'balls5n.txt'

    CWD_PATH = os.getcwd()
    PATH_TO_LABELS = os.path.join(CWD_PATH,model_name,model_labels)
    PATH_TO_YOLOV5_GRAPH = os.path.join(CWD_PATH,model_name,yolov5_model)

    # Import Labels File
    with open(PATH_TO_LABELS, 'r') as f:
        labels = [line.strip() for line in f.readlines()]

    # Initialize Yolov5
    model = yolov5.load(PATH_TO_YOLOV5_GRAPH)

    min_conf_threshold = 0.25
    # set model parameters
    model.conf = 0.25  # NMS confidence threshold
    model.iou = 0.45  # NMS IoU threshold
    model.agnostic = False  # NMS class-agnostic
    model.multi_label = True # NMS multiple labels per box
    model.max_det = 1000  # maximum number of detections per image

    frame = img.copy()
    results = model(frame)
    predictions = results.pred[0]

    boxes = predictions[:, :4]
    scores = predictions[:, 4]
    classes = predictions[:, 5]
    # Draws Bounding Box onto image
    results.render() 

    # Initialize frame rate calculation
    frame_rate_calc = 30
    freq = cv2.getTickFrequency()

    frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #imW, imH = int(400), int(300)
    imW, imH = int(640), int(640)
    frame_resized = cv2.resize(frame_rgb, (imW, imH))
    input_data = np.expand_dims(frame_resized, axis=0)

    max_score = 0
    max_index = 0
    
    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(scores)):
        curr_score = scores.numpy()
        # Found desired object with decent confidence
        if ((labels[int(classes[i])] == cType.getType()) and (curr_score[i] > max_score) and (curr_score[i] > min_conf_threshold) and (curr_score[i] <= 1.0)):
            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            xmin = int(max(1,(boxes[i][0])))
            ymin = int(max(1,(boxes[i][1])))
            xmax = int(min(imW,(boxes[i][2])))
            ymax = int(min(imH,(boxes[i][3])))
                       
            # Draw label
            object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
            label = '%s: %d%%' % (object_name, int(curr_score[i]*100)) # Example: 'person: 72%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
            #cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
            #cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
            cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text
            #if cType.getType() == "ball":
                
            # Record current max
            max_score = curr_score[i]
            max_index = i

    # Write Image (with bounding box) to file
    cv2.imwrite('video.jpg', frame)

if __name__ == '__main__':
    cType.setType("balls")
    img = cv2.imread('image.jpg')
    find_ball(img)

import yolov5
import cv2
import numpy as np
import os
import statistics
import math


model_name = 'yolo5_model'
yolov5_model = 'balls5n.pt'
model_labels = 'balls5n.txt'
CWD_PATH = os.getcwd()
PATH_TO_LABELS = os.path.join(CWD_PATH,model_name,model_labels)
PATH_TO_YOLOV5_GRAPH = os.path.join(CWD_PATH,model_name,yolov5_model)
imageSavePath = '/home/circlekenjoyers/Freenove_4WD_Smart_Car_Kit_for_Raspberry_pi/Code/Server/imageProcessed.jpeg'
global cType
from camera import Camera


def find_ball(img,designatedColor):
    frame = img
    hueValue = 0
    #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


    # model_name = 'yolo5_model'
    # yolov5_model = 'balls5n.pt'
    # model_labels = 'balls5n.txt'


    # CWD_PATH = os.getcwd()
    # PATH_TO_LABELS = os.path.join(CWD_PATH,model_name,model_labels)
    # PATH_TO_YOLOV5_GRAPH = os.path.join(CWD_PATH,model_name,yolov5_model)


    # Import Labels File
    with open(PATH_TO_LABELS, 'r') as f:
        labels = [line.strip() for line in f.readlines()]


    # Initialize Yolov5
    model = yolov5.load(PATH_TO_YOLOV5_GRAPH)


    stride, names, pt = model.stride, model.names, model.pt
    print('stride = ',stride, 'names = ', names)
    #model.warmup(imgsz=(1 if pt else bs, 3, *imgsz))  # warmup


    min_conf_threshold = 0.25
    # set model parameters
    model.conf = 0.40  # NMS confidence threshold
    model.iou = 0.45  # NMS IoU threshold
    model.agnostic = False  # NMS class-agnostic
    model.multi_label = True # NMS multiple labels per box
    model.max_det = 1000  # maximum number of detections per image


    results = model(frame)
    predictions = results.pred[0]
    ballFound = False
    boxes = predictions[:, :4]
    scores = predictions[:, 4]
    classes = predictions[:, 5]
    # Draws Bounding Box onto image
    results.render()


    # Initialize frame rate calculation
    frame_rate_calc = 30
    freq = cv2.getTickFrequency()


    #imW, imH = int(400), int(300)
    imW, imH = int(640), int(640)
    #frame_resized = cv2.resize(frame_rgb, (imW, imH))
    #input_data = np.expand_dims(frame_resized, axis=0)


    max_score = 0
    max_index = 0
   
    print(f'Length of scores: {len(scores)}')
    # Loop over all detections and draw detection box if confidence is above minimum threshold
    for i in range(len(scores)):
        curr_score = scores.numpy()
        ballColor = None
       
        # Found desired object with decent confidence
        if ((curr_score[i] > min_conf_threshold) and (curr_score[i] <= 1.0)):
            print('Class: ',labels[int(classes[i])],' Conf: ', curr_score[i])


            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            xmin = int(max(1,(boxes[i][0])))
            ymin = int(max(1,(boxes[i][1])))
            xmax = int(min(imW,(boxes[i][2])))
            ymax = int(min(imH,(boxes[i][3])))


            xminSmall = int(xmin + ((xmax - xmin) / 4))
            xmaxSmall = int(xmin + (((xmax - xmin) / 4) * 3))


            yminSmall = int(ymin + ((ymax - ymin) / 4))
            ymaxSmall = int(ymin + (((ymax - ymin) / 4) * 3))
                       
            # frame appears to use y-x coordinates when compared to a JPEG viewer
            croppedImage = frame[yminSmall:ymaxSmall,xminSmall:xmaxSmall]


            print(f'ymin: {ymin} xmin: {xmin} ymax: {ymax} xmax: {xmax}')


            xCenter = int(xmin + ((xmax - xmin) / 2))
            yCenter = int(ymin + ((ymax - ymin) / 2))


            print(f'xCenter: {xCenter} yCenter: {yCenter}')


            hsv_pixel = cv2.cvtColor(croppedImage, cv2.COLOR_BGR2HSV)            
            print(hsv_pixel.ndim)
            print("\n-------------------------------------\n")


            myList = []


            x = len(hsv_pixel)
            y = len(hsv_pixel[0])


            # if (x < 40 and y < 40) or (x >225 and y > 225):
            #     print("False , None, 0, 0")
            #     return False, 0, 0, 0
           
            print(f'X Length: {x} Y length: {y}' )


            for p in range(x - 1):
                for j in range(y - 1):
                    myList.append(hsv_pixel[p][j][0])
                       
            sumHue = sum(myList)
            hueValue = math.floor(sumHue / len(myList))
            print(hueValue)
           


            if 121 <= hueValue <= 185:


                ballColor = "red"


            elif 90 <= hueValue <= 120:


                ballColor = "blue"


            elif 61 <= hueValue <= 89:


                ballColor = "green"


            elif 20 <= hueValue <= 60:


                ballColor = "yellow"


            print(ballColor)
            print(designatedColor)
            if ballColor != designatedColor:
 
                print(f"Not saving picture: For loop value: {i}")
                cv2.circle(img, center = (xCenter, yCenter), radius = 10, color = (255,255,255), thickness=2)
                cv2.imwrite(imageSavePath, img)
                
            
            ballDistance = 0

            if yCenter > 257:
                ballDistance = round(5.47 + (0.145 * (260 - yCenter)))
            elif yCenter >= 219 and yCenter <= 257:
                ballDistance = round(6.13 + (0.322 * (257 - yCenter)))
            elif yCenter < 219 and yCenter > 215:
                ballDistance = round(18.77 + (0.38 * (218 - yCenter)))
            elif yCenter >= 196 and yCenter <= 215:
                 ballDistance = round(19.92 + (2.3 * (215 - yCenter)))
            else:
                ballDistance = 55
            # print(hue_channel)
           
       




            # print(type(hueValue))
            # print("My value: ", hueValue)
           


            # Draw label  


            object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
            label = '%s: %d%%: %s :%d %s: %d' % (object_name, int(curr_score[i]*100),"hue_value", hueValue, "IN", ballDistance) # Example: 'person: 72%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
            label_ymin = max(yminSmall, labelSize[1] + 10) # Make sure not to draw label too close to top of window
            cv2.rectangle(img, (xminSmall,yminSmall), (xmaxSmall,ymaxSmall), (10, 255, 0), 2)
            # cv2.rectangle(img, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
            cv2.putText(img, label, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2) # Draw label text
            #if cType.getType() == "ball":
            cv2.circle(img, center = (xCenter, yCenter), radius = 10, color = (255,255,255), thickness=2)
            ballFound = True

            # Record current max
            max_score = curr_score[i]
            max_index = i
            cv2.imwrite(imageSavePath, img)

            


            return ballFound, hueValue, xCenter, yCenter
            # return hueValue


    return False, hueValue, 0, 0


if __name__ == '__main__':
    #cType.setType("balls")
    img = cv2.imread('/home/circlekenjoyers/Freenove_4WD_Smart_Car_Kit_for_Raspberry_pi/Code/Server/image.jpg')
    find_ball(img)




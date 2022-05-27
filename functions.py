from unittest import result
import cv2
from matplotlib.transforms import Bbox
import mediapipe as mp
from google.protobuf.json_format import MessageToDict

class handDetector():
    def __init__(self, mode = False, maxHands = 2, detectionCon = 0.5, trackCon = 0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode,
                      max_num_hands=self.maxHands,
                      min_detection_confidence=self.detectionCon,
                      min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
    
    def findHands(self,img, draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img
    
    def findIndex(self, img, draw = True) :
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        h, w, c = img.shape
        pos = []
        xList = []
        yList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[0]
            for id, lm in enumerate(myHand.landmark):
                if (id > 5 and id <= 8):
                    # print(f'Id: {id}, x: {lm.x}, y: {lm.y}')
                    px, py, pz = int(lm.x*w), int(lm.y*h), int(lm.z*w)
                    xList.append(px)
                    yList.append(py)
                    if id == 8: 
                        pos.append(lm)
            
            #Box
            xMin, xMax = min(xList), max(xList)
            yMin, yMax = min(yList), max(yList)
            boxW, boxH = xMax - xMin, yMax - yMin
            bbox  = xMin, yMin, boxW, boxH

            if draw:
                self.mpDraw.draw_landmarks(img, myHand, self.mpHands.HAND_CONNECTIONS)
                cv2.rectangle(img, (bbox[0] - 10, bbox[1] - 10),
                                (bbox[0] + bbox[2] + 10, bbox[1] + bbox[3] + 10),
                                (255, 0, 255), 2)
        return pos, img                                

    def findPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results.multi_hand_landmarks:
            # print(f'n = {len(self.results.multi_hand_landmarks)}')
            myHand = self.results.multi_hand_landmarks[handNo]
            myHandReal = self.results.multi_hand_world_landmarks[handNo]
            # print(f'N_Landmark = {len(myHand.landmark)}')
            # print(f'Index_Finger_Pos = {myHand.landmark[8]}')
            # print(f'Index_Finger_Pos_Real = {myHandReal.landmark[8]}')
            for id, lm in enumerate(myHand.landmark): #draw circle in every finger landmarks
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h) #get a landmark position based on screen wide
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 3, (255, 0, 255), cv2.FILLED)
        return lmList

    def detectHandNum(self, img):
        if self.results.multi_hand_landmarks:
            h, w, c = img.shape
            #display both hands
            if len(self.results.multi_handedness) == 2:
                cv2.putText(img, 'Both Hands', (250, h-20), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)
            else:
                for i in self.results.multi_handedness:
                    label = MessageToDict(i)['classification'][0]['label']
                    if label == "Left":
                        cv2.putText(img, 'Right Hand', (20, h-20), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)
                    if label == "Right":
                        cv2.putText(img, 'Left Hand', (460, h-20), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)
        return img
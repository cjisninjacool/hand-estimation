import cv2
import mediapipe as mp
import math
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands



paused = True



def distanceBetween(x1,y1,x2,y2):
    dis1 = (x2 - x1) **2
    dis2 = (y2 - y1) **2
    return math.sqrt(dis1 + dis2)

def extendedornah(finger,sensitivity):
    one_dis =  distanceBetween(finger[3].x,finger[3].y,finger[2].x,finger[2].y)
    two_dis = distanceBetween(finger[2].x,finger[2].y,finger[1].x,finger[1].y)
    three_dis = distanceBetween(finger[1].x,finger[1].y,finger[0].x,finger[0].y)
    dis = one_dis+two_dis+three_dis
    dis = dis/3
    dis = round(dis*100)
    if dis < sensitivity:
        return [False,dis]
    if dis > sensitivity:
        return [True,dis]
    

    

import time
cap = cv2.VideoCapture(0)
prevTime = 0
with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_hands=1 ) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      continue

    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        
        thumb = [hand_landmarks.landmark[1],hand_landmarks.landmark[2],hand_landmarks.landmark[3],hand_landmarks.landmark[4]]
        index = [hand_landmarks.landmark[5],hand_landmarks.landmark[6],hand_landmarks.landmark[7],hand_landmarks.landmark[8]]
        middle= [hand_landmarks.landmark[9],hand_landmarks.landmark[10],hand_landmarks.landmark[11],hand_landmarks.landmark[12]]
        ring = [hand_landmarks.landmark[13],hand_landmarks.landmark[14],hand_landmarks.landmark[15],hand_landmarks.landmark[16]]
        pinky = [hand_landmarks.landmark[17],hand_landmarks.landmark[18],hand_landmarks.landmark[19],hand_landmarks.landmark[20]]
        hand = {
            "Thumb":thumb,
            "Index":index,
            "Middle":middle,
            "Ring":ring,
            "Pinky":pinky
            }
        total = 0
        if extendedornah(hand["Pinky"],4)[0] == False and paused == False:
            print("Pause")
            paused = True
            play = True
        if extendedornah(hand["Index"],4)[0] == False and played == False:
            print("Play")
            played = True
            paused = false

        



        mp_drawing.draw_landmarks(
            image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    currTime = time.time()
    fps = 1 / (currTime - prevTime)
    prevTime = currTime
    cv2.putText(image, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 196, 255), 2)
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()

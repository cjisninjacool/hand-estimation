import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
import math



from pycaw.pycaw import AudioUtilities


class AudioController(object):
    def __init__(self, process_name):
        self.process_name = process_name
        self.volume = self.process_volume()

    def mute(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                interface.SetMute(1, None)
                print(self.process_name, 'has been muted.')  # debug

    def unmute(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                interface.SetMute(0, None)
                print(self.process_name, 'has been unmuted.')  # debug

    def process_volume(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                print('Volume:', interface.GetMasterVolume())  # debug
                return interface.GetMasterVolume()

    def set_volume(self, decibels):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                # only set volume in the range 0.0 to 1.0
                self.volume = min(1.0, max(0.0, decibels))
                interface.SetMasterVolume(self.volume, None)
                print('Volume set to', self.volume)  # debug

    def decrease_volume(self, decibels):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                # 0.0 is the min value, reduce by decibels
                self.volume = max(0.0, self.volume-decibels)
                interface.SetMasterVolume(self.volume, None)
                print('Volume reduced to', self.volume)  # debug

    def increase_volume(self, decibels):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            interface = session.SimpleAudioVolume
            if session.Process and session.Process.name() == self.process_name:
                # 1.0 is the max value, raise by decibels
                self.volume = min(1.0, self.volume+decibels)
                interface.SetMasterVolume(self.volume, None)
                print('Volume raised to', self.volume)  # debug




# For static images:
IMAGE_FILES = []
with mp_hands.Hands(static_image_mode=True,max_num_hands=1,min_detection_confidence=0.7) as hands:
  for idx, file in enumerate(IMAGE_FILES):
    # Read an image, flip it around y-axis for correct handedness output (see
    # above).
    image = cv2.flip(cv2.imread(file), 1)
    height,width,channels = image.shape
    # Convert the BGR image to RGB before processing.
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Print handedness and draw hand landmarks on the image.
    print('Handedness:', results.multi_handedness)
    if not results.multi_hand_landmarks:
      continue
    image_height, image_width, _ = image.shape
    annotated_image = image.copy()
    for hand_landmarks in results.multi_hand_landmarks:
      print('hand_landmarks:', hand_landmarks)
      print(
          f'Index finger tip coordinates: (',
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
      )
      mp_drawing.draw_landmarks(
          annotated_image,
          hand_landmarks,
          mp_hands.HAND_CONNECTIONS,
          mp_drawing_styles.get_default_hand_landmarks_style(),
          mp_drawing_styles.get_default_hand_connections_style())
    cv2.imwrite(
        '/tmp/annotated_image' + str(idx) + '.png', cv2.flip(annotated_image, 1))

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    min_detection_confidence=0.8,min_tracking_confidence=0.7) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    audio_controller = AudioController('chrome.exe')

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      height,width,channels = image.shape

      for hand_landmarks in results.multi_hand_landmarks:
        
        thumb = hand_landmarks.landmark[4]
        index = hand_landmarks.landmark[8]
        middle = hand_landmarks.landmark[12]
        ring = hand_landmarks.landmark[16]
        pinky =hand_landmarks.landmark[20]
        palm = hand_landmarks.landmark[0]

        x1 = thumb.x
        y1 = thumb.y
        x2 = index.x
        y2 = index.y
        distance_1 = (x2 - x1)**2
        distance_2 = (y2 - y1)**2
        distance = math.sqrt(distance_1+distance_2)
        thumb_pos = (x1 * width,y1 * height)
        pointer_pos = (x2 * width,y2 * height)
        thumb_pos = (round(thumb_pos[0]),round(thumb_pos[1]))
        pointer_pos = (round(pointer_pos[0]),round(pointer_pos[1]))
        image = cv2.line(image,thumb_pos,pointer_pos,(255,0,0),9)
        x1 = thumb_pos[0]
        y1 = thumb_pos[1]
        x2 = pointer_pos[0]
        y2 = pointer_pos[1]
        distance_1 = (x2 - x1) **2
        distance_2 = (y2 - y1)**2
        distance = math.sqrt(distance_1+distance_2) - 20
        distance = distance * 0.7
        if (distance >= 100):
            distance = 100
        if distance <= 0:
            distance = 0
        distance = (round(distance))/100
        audio_controller.set_volume(distance)

        x1 = middle.x
        x2 = ring.x
        y1 = middle.y
        y2 = ring.y
        distance_1 = (x2-x1)**2
        distance_2 = (y2-y1)**2
        distance = math.sqrt(distance_1+distance_2)
        disstance_total = (round(distance*1000))

        x1 = thumb.x
        x2 = ring.x
        y1 = thumb.y
        y2 = ring.y
        distance_1 = (x2-x1)**2
        distance_2 = (y2-y1)**2
        distance = math.sqrt(distance_1+distance_2)
        distance = (round(distance*1000))
        disstance_total = distance + disstance_total
        disstance_total = (round(disstance_total/2))
        if disstance_total < 50:
            print("mute")
            audio_controller.mute()
        else:
            print("unmute")
            audio_controller.unmute()


        current_dist = ()
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
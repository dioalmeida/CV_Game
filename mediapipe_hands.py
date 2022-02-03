import cv2
import mediapipe as mp
from dataclasses import dataclass
from dataclasses import field
import math

@dataclass
class HandMeasures:
    hand: list = field(default_factory=list)
    visible: bool = False
    vertical_thumb_distance: float = 0.0
    horizontal_thumb_distance: float = 0.0


class detection:
    def __init__(self):
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_hands = mp.solutions.hands


        self.drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        self.cap = cv2.VideoCapture(0)
        self.hands = mp_hands.Hands(
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.7)

        self.handMeasures = {'Left': HandMeasures(),
                    'Right': HandMeasures()}

    


    def euclidian(landmarkA, landmarkB):
        return math.sqrt((landmarkA.x - landmarkB.x) ** 2 +
                        (landmarkA.y - landmarkB.y) ** 2 +
                        (landmarkA.z - landmarkB.z) ** 2)

    def computeDistances_hand(self,hand):
        handMeasures = HandMeasures()


        handMeasures.vertical_thumb_distance=hand.landmark[4].y-hand.landmark[2].y #up/down
        handMeasures.horizontal_thumb_distance = hand.landmark[4].x-hand.landmark[2].x #left/right
        #handMeasures.dist_thumb_pointer = euclidian(hand.landmark[4], hand.landmark[8])
        #handMeasures.dist_thumb_basepointer = euclidian(hand.landmark[4], hand.landmark[5])

        return handMeasures

    def ProcessHandData(self,results_hands):
        """ Deal with discovering which hands are visible and computing some data for them """

        self.handMeasures['Left'].visible = self.handMeasures['Right'].visible = False

        if results_hands.multi_hand_landmarks != None:
            for hand, handedness in zip(results_hands.multi_hand_landmarks, results_hands.multi_handedness):
                self.handMeasures[handedness.classification[0].label] = self.computeDistances_hand(hand)
                self.handMeasures[handedness.classification[0].label].visible = True
                self.handMeasures[handedness.classification[0].label].hand = hand

        return self.handMeasures

    def HandDataDecision(self,handData):
        decisions={"Left":0, "Right":0, "Jump":0}
        #print(handData.vertical_thumb_distance)
        if handData.horizontal_thumb_distance <=-0.04:
            #print("left")
            decisions["Left"]=1
        elif handData.horizontal_thumb_distance >=0.035:
            #print("right")
            decisions["Right"]=1
        #print(handData.vertical_thumb_distance)
        if handData.vertical_thumb_distance > -0.055:
            #print("jump")
            decisions["Jump"]=1

        return decisions

        
    """
    # For webcam input:
    def runDetection(cap,show=False):
    
        with mp_hands.Hands(
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.7) as hands:
        
            while cap.isOpened():
                success, image = cap.read()
                image = cv2.flip(image, 1)
                if not success:
                    print("Ignoring empty camera frame.")
                # If loading a video, use 'break' instead of 'continue'.
                    continue

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results_hands = hands.process(image)

                handMeasures = ProcessHandData(results_hands)

            
                if handMeasures['Right'].visible:
                    DATA_DECISION=HandDataDecision(handMeasures['Right'])
                    print(DATA_DECISION)
            
                
                if show:
                    image.flags.writeable = True
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    if results_hands.multi_hand_landmarks:
                        for hand_landmarks in results_hands.multi_hand_landmarks:
                            mp_drawing.draw_landmarks(
                                image,
                                hand_landmarks,
                                mp_hands.HAND_CONNECTIONS,
                                mp_drawing_styles.get_default_hand_landmarks_style(),
                                mp_drawing_styles.get_default_hand_connections_style())
                

                    # Flip the image horizontally for a selfie-view display.
                    cv2.imshow('MediaPipe Hands', image)
                    if cv2.waitKey(5) & 0xFF == 27:
                        break
                
        cap.release()
    """
    def get_frame(self):
        DATA_DECISION={"Left":0, "Right":0, "Jump":0}
        success, image = self.cap.read()
        image = cv2.flip(image, 1)
        if not success:
            print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
            

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results_hands = self.hands.process(image)

        handMeasures = self.ProcessHandData(results_hands)


        if handMeasures['Right'].visible:
            DATA_DECISION=self.HandDataDecision(handMeasures['Right'])
            #print(DATA_DECISION)
        return DATA_DECISION
        """
        
        if show:
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results_hands.multi_hand_landmarks:
                for hand_landmarks in results_hands.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing_styles.get_default_hand_landmarks_style(),
                        mp_drawing_styles.get_default_hand_connections_style())
        

            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MediaPipe Hands', image)
        """
            
    """
    while True:
        get_frame(cap, hands, show=True)
    """

#test = detection()
#while True:
#    test.get_frame()
import cv2, mediapipe as mp

class HandTracker:
    def __init__(self):
        self.cap=cv2.VideoCapture(0)
        self.hands=mp.solutions.hands.Hands(max_num_hands=1)
        self.cx=640; self.cy=360
    def update(self,w,h):
        ok,frame=self.cap.read()
        if not ok: return None,False,False
        frame=cv2.flip(frame,1)
        res=self.hands.process(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
        fist=False
        detected=False
        if res.multi_hand_landmarks:
            detected=True
            hand=res.multi_hand_landmarks[0]
            p=hand.landmark[9]
            x,y=int(p.x*w),int(p.y*h)
            self.cx+=(x-self.cx)*0.25; self.cy+=(y-self.cy)*0.25
            folded=sum(hand.landmark[t].y>hand.landmark[t-2].y for t in [8,12,16,20])
            fist=folded>=4
        return (self.cx,self.cy),fist,detected
    def release(self): self.cap.release()

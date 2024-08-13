import torch
from ultralytics import YOLO
import cv2

model = YOLO('best2.pt')
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    
    if not ret:
        break
    
    results = model(frame)
    
    for result in results:
        boxes = result.boxes
        
        if len(boxes) > 0:
            print("Fuoco rilevato!")
        else: print("NULLA")    

        annotated_frame = results[0].plot()
        
        cv2.imshow("Rilevamento Fuoco", annotated_frame)
    
    #Esci con q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

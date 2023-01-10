import numpy as np
import cv2, time , datetime


cap = cv2.VideoCapture(0)

#Cascade Classifiers for face and body
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")

detection = False
detection_stopped_time = None
timer_stated = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5

#3 and 4 is width and height properties
frame_size = (int(cap.get(3)), int(cap.get(4)))
#records video
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #1.3 scalefactor for fast and accurate detection
    #5 minNeighbour for better quality/accuracy
    #detect face and body
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    bodies = body_cascade.detectMultiScale(gray, 1.1, 5)

    if len(faces) + len(bodies) >0:
        #keeps recording, resets timer
        if detection:
            timer_stated = False
        #starts initial recording           
        else:
            detection = True
            current_time = datetime.datetime.now().strftime("%d-%M-%Y-%H-%M-%S")
            out = cv2.VideoWriter(f"{current_time}.mp4", fourcc, 20.0, frame_size)
            print("Started Recording")
    #starts timer when body or face not in frame
    elif detection:
        #if timer expires stops recording
        if timer_stated:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection = False
                timer_stated = False
                out.release()
                print("Stop Recording")
        #starts timer
        else:
            timer_stated = True
            detection_stopped_time = time.time()

    
    if detection:
        out.write(frame)


    #for (x, y, w, h) in faces:
        #draws a blue rectangle on the face
    #    cv2.rectangle(frame, (x,y), (x+w, y+h), (255, 0, 0), 3)

    
    cv2.imshow("Camera", frame)

    #quits showing cam when q pressed
    if cv2.waitKey(1) == ord('q'):
        break

out.release()
cap.release()
cv2.destroyAllWindows
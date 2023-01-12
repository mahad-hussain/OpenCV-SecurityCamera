import numpy as np
import cv2, time , datetime
import smtplib
from email.message import EmailMessage
import glob

"""
Function that sends an email alert with the video attached
@param subject (str): contains the subject of the email
@param subject (str): contains the subject of the email
@param body (str): contains the body of the email
@param to (str): contains the email address which the email needs to be sent to
@param file (str): contains the subject of the email
"""
def email_alert(subject, body, to, file):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    
    with open(file, "rb") as f:
        file_data = f.read()
        #print("File data in binary", file_data)
        file_name = f.name
        #print("File name is", file_name)
        msg.add_attachment(file_data, maintype="application", subtype = "jpg", filename = file_name)

    user = "user@gmail.com"
    msg['from'] = user
    password = "password"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user,password)
    server.send_message(msg)

    server.quit()
    


status = 1
# mouse callback function
def mouse_func(event,x,y,flags,param):
    global status
    if event == cv2.EVENT_LBUTTONDOWN:
        status = 0
        print("Closing application")

cap = cv2.VideoCapture(0)

cv2.namedWindow('Camera')
cv2.setMouseCallback('Camera',mouse_func)

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

#list of videos
orig_videos = glob.glob("*.mp4")

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
            file_name = f"{current_time}.mp4"
            out = cv2.VideoWriter(file_name, fourcc, 20.0, frame_size)
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
    
    
    cv2.imshow("Camera", frame)

    #quits showing cam when q pressed
    if cv2.waitKey(1) == ord('q') or status == 0:
        break

email_alert(f"Alert", f"Someone has entered your room! Attached below is: {str(file_name)}, which contains the footage."
,"gmail", file_name)
out.release()
cap.release()
cv2.destroyAllWindows

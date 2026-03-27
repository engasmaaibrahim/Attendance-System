#########################
# Import Libraries
#########################
import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime
import pandas as pd
import os
from scipy.spatial import distance as dist


#########################
# Blink and Blur Variables
#########################
PROCESS_RES = 0.25
CONFIDENCE_THRESHOLD = 0.6
BLUR_THRESHOLD = 100
EYE_AR_THRESH = 0.22
EYE_AR_CONSEC_FRAMES = 2
blink_data = {}



########################
# 1- Load Stored Faces
########################

path = 'ImagesAttendance'
def load_images(path):
    images = []
    classNames = []

    for file in os.listdir(path):
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = cv2.imread(f"{path}/{file}")
            if img is not None:
                images.append(img)
                classNames.append(os.path.splitext(file)[0].upper())

    return images, classNames
        
########################
# 2- Encode Stored Faces
########################
def findEncodings(images, classNames):
    encodeList = []
    validNames = []
    for img , name in zip(images, classNames): # Loop through the images:
        # Convert image from BGR (OpenCV) to RGB (face_recognition)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Get face encodings (128-d feature vector)
        encodes = face_recognition.face_encodings(img)
        
        if len(encodes) > 0:
            encodeList.append(encodes[0]) # Take first face only
            validNames.append(name) # Store corresponding name
        else:
            print('No face found')
    return encodeList, validNames



#############################
# 3- Mark Attendance in Excel
#############################
def markAttendance(name):
    file_name = 'Attendance.xlsx'
    
    # Read excel file
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
    else:
        # Create empty DataFrame if file doesn't exist
        df = pd.DataFrame(columns=['Name', 'Date' ,'Time'])
    
    now = datetime.now()
    date_str = now.strftime('%Y-%m-%d')
    time_str = now.strftime('%H:%M:%S')

    if not ((df['Name'] == name) & (df['Date'] == date_str)).any():
        new_row = pd.DataFrame([[name, date_str, time_str]],
                               columns=['Name', 'Date', 'Time'])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(file_name, index=False)


#########################
# 4- Eye Aspect Ratio
########################
def calculate_ear(eye):
    # Vertical distances
    v1 = dist.euclidean(eye[1], eye[5])
    v2 = dist.euclidean(eye[2], eye[4])
    # Horizontal distance
    h = dist.euclidean(eye[0], eye[3])
    ear = (v1 + v2) / (2.0 * h)
    return ear
        

########################
# Initialization
########################
images, classNames = load_images(path)
encodeListKnown, classNames = findEncodings(images, classNames)

cap = cv2.VideoCapture(0)
markedNames = set()

# Set window size
cv2.namedWindow('Smart Attendance', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Smart Attendance', 1200, 800)


########################
# Main Loop
########################
        
while True:
    success, img = cap.read()
    
    if not success or img is None:
        continue
    
    # resize image for faster processing
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    # Convert image from BGR (OpenCV) to RGB (face_recognition)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    
    # Blur Detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_value = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Get the detected face locations
    facesCurFrame = face_recognition.face_locations(imgS)
    
    # Get the detected face the encodings
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
       
    # Get landmarks for blink detection
    face_landmarks_list = face_recognition.face_landmarks(imgS, facesCurFrame)

    for encodeFace, faceLoc, landmarks in zip(encodesCurFrame, facesCurFrame, face_landmarks_list):
        
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)
        
        # Scale coordinates
        top, right, bottom, left = faceLoc
        top, right, bottom, left = top*4, right*4, bottom*4, left*4
        
        # Default values
        name = "Unknown"
        color = (0, 0, 255)
        
        if matches[matchIndex] and faceDis[matchIndex] < CONFIDENCE_THRESHOLD:

            person_id = classNames[matchIndex]

            # Initialize blink data
            if person_id not in blink_data:
                blink_data[person_id] = {"frames": 0, "count": 0}

            # Blink detection
            leftEye = landmarks['left_eye']
            rightEye = landmarks['right_eye']

            ear = (calculate_ear(leftEye) + calculate_ear(rightEye)) / 2.0

            if ear < EYE_AR_THRESH:
                blink_data[person_id]["frames"] += 1
            else:
                if blink_data[person_id]["frames"] >= EYE_AR_CONSEC_FRAMES:
                    blink_data[person_id]["count"] += 1
                blink_data[person_id]["frames"] = 0

            blink_count = blink_data[person_id]["count"]

            # Decision
            if blink_count >= 1 and blur_value <  BLUR_THRESHOLD:
                name = person_id
                color = (0, 255, 0)

                if name not in markedNames:
                    markAttendance(name)
                    markedNames.add(name)

            elif blink_count < 1:
                name = "BLINK TO VERIFY"
                color = (255, 255, 0)

            else:
                name = "LOW QUALITY"
                color = (0, 165, 255)        
    
        # Draw
        cv2.rectangle(img, (left, top), (right, bottom), color, 2)
        cv2.rectangle(img, (left, bottom-35), (right, bottom), color, cv2.FILLED)

        cv2.putText(img, name, (left+6, bottom-6),
                    cv2.FONT_HERSHEY_COMPLEX, 0.7, (255,255,255), 2)

        if matches[matchIndex]:
            person_id = classNames[matchIndex]
            if person_id in blink_data:
                cv2.putText(img, f'Blinks: {blink_data[person_id]["count"]}',
                            (left, top-30), cv2.FONT_HERSHEY_PLAIN, 1, color, 1)

        cv2.putText(img, f'Blur: {int(blur_value)}',
                    (left, top-10), cv2.FONT_HERSHEY_PLAIN, 1, color, 1)

    cv2.imshow('Smart Attendance', img)
    
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows() 
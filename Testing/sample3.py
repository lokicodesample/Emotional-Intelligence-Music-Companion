import cv2
import numpy as np
from keras.models import model_from_json
import time
emotion_label = {0:"angry",1:"happy",2:"neutral",3:"sad"}
a=0
b=0
c=0
d=0

# load json and create model
json_file = open('../Models/emotion_model_xception.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
emotion_model = model_from_json(loaded_model_json)

# load weights into new model
emotion_model.load_weights("Models/emotion_model_xception.h5")

cap=cv2.VideoCapture(0)
print("Camera is now Capturing Emotion")

"""cap=cv2.VideoCapture("Videos/videoplayback.mp4")
print("In Video now Capturing Emotion")"""

emotions_count = {label: 0 for label in emotion_label.values()}  # Initialize count for each emotion
start_time = time.time()
stable_prediction_time = 20

while True:

    ret,frame =cap.read()
    gray_cvt_frame= cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    if not ret:
        break
    face_detector = cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')
    # detect faces available on camera
    num_faces = face_detector.detectMultiScale(gray_cvt_frame, scaleFactor=1.3, minNeighbors=5)

    # take each face available on the camera and Preprocess it
    for (x, y, w, h) in num_faces:
        cv2.rectangle(frame, (x, y-50), (x+w, y+h+10), (0, 255, 0), 4)
        roi_gray_frame = gray_cvt_frame[y:y + h, x:x + w]
        #cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (48, 48)), -1), 0)
        cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (71, 71)), -1), 0)

        # predict the emotions
        emotion_prediction = emotion_model.predict(cropped_img)
        maxindex = int(np.argmax(emotion_prediction))
        cv2.putText(frame, emotion_label[maxindex], (x+5, y-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
        print(emotion_label[maxindex])
        if emotion_label[maxindex] == 'angry':
                a+=1
                print(a)
        elif emotion_label[maxindex]=='happy':
                b+=1
        elif emotion_label[maxindex] == 'neutral':
                c += 1
        elif emotion_label[maxindex]=='sad':
                d+=1
        else:
                pass
    cv2.imshow('Emotion Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# Check if stable_prediction_time seconds have passed
    if time.time() - start_time >= stable_prediction_time:
        break

max_count_emotion = max(a, b, c, d)
if max_count_emotion == a:
    final_emotion = "angry"
elif max_count_emotion == b:
    final_emotion = "happy"
elif max_count_emotion == c:
    final_emotion = "neutral"
else:
    final_emotion = "sad"
print("Final Emotion:", final_emotion)

cap.release()
cv2.destroyAllWindows()

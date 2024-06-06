import cv2
import numpy as np
from keras.models import model_from_json
import time

emotion_label = {0: "angry", 1: "happy", 2: "neutral", 3: "sad"}

# Load json and create model
json_file = open('../Models/emotion_model_xception.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
emotion_model = model_from_json(loaded_model_json)

# Load weights into new model
emotion_model.load_weights("Models/emotion_model_xception.h5")

cap = cv2.VideoCapture(0)
print("Camera is now Capturing Emotion")

"""cap=cv2.VideoCapture("Videos/videoplayback.mp4")
print("In Video now Capturing Emotion")"""

# Initialize count for each emotion
emotions_count = {label: 0 for label in emotion_label.values()}

start_time = time.time()
stable_prediction_time = 20

while True:
    ret, frame = cap.read()
    gray_cvt_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if not ret:
        break
    face_detector = cv2.CascadeClassifier('Haarcascades/haarcascade_frontalface_default.xml')

    # Detect faces available on camera
    num_faces = face_detector.detectMultiScale(gray_cvt_frame, scaleFactor=1.3, minNeighbors=5)

    # Take each face available on the camera and preprocess it
    for (x, y, w, h) in num_faces:
        cv2.rectangle(frame, (x, y - 50), (x + w, y + h + 10), (0, 255, 0), 4)
        roi_gray_frame = gray_cvt_frame[y:y + h, x:x + w]
        cropped_img = np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame, (71, 71)), -1), 0)

        # Predict the emotions
        emotion_prediction = emotion_model.predict(cropped_img)
        maxindex = int(np.argmax(emotion_prediction))

        # Update count for detected emotion
        emotions_count[emotion_label[maxindex]] += 1

        # Draw the detected emotion label on the frame
        cv2.putText(frame, emotion_label[maxindex], (x + 5, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2,
                    cv2.LINE_AA)

    cv2.imshow('Emotion Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Check if stable_prediction_time seconds have passed
    if time.time() - start_time >= stable_prediction_time:
        break

# Determine the final emotion based on the maximum count
print(f"Emotion Count: {emotions_count}")
final_emotion = max(emotions_count, key=emotions_count.get)
print("Final Emotion:", final_emotion)
cap.release()
cv2.destroyAllWindows()



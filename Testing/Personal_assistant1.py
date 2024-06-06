import cv2
import numpy as np
from keras.models import model_from_json
import time
import speech_recognition as sr
import pyttsx3
import pywhatkit

emotion_label = {0: "angry", 1: "happy", 2: "neutral", 3: "sad"}

# Load json and create model
json_file = open('Models/emotion_model_xception.json', 'r')
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
emotion_pred = max(emotions_count, key=emotions_count.get)
print("Final Emotion:", emotion_pred)
cap.release()
cv2.destroyAllWindows()


player = pyttsx3.init()
listener = sr.Recognizer()


def listen():
    with sr.Microphone() as input_device:
        listener.adjust_for_ambient_noise(input_device)
        talk("Started listening...")
        try:
            voice_content = listener.listen(input_device, timeout=5)  # Listening for 10 seconds
            text = listener.recognize_google(voice_content)
            text = text.lower()
            print(text)
            return text
        except sr.WaitTimeoutError:
            talk("Timeout reached. No speech detected.")
            return ""
        except sr.UnknownValueError:
            talk("Sorry, I couldn't understand what you said.")
            return ""


def talk(text):
    print(text)
    player.say(text)
    player.runAndWait()


def lokiBot(mode, def_lang):
    comment = listen()
    if "loki" in comment:
        comment = comment.replace("loki", "")
        if "yes" in comment:
            lang = "Which language do you need?"
            talk(lang)
            def_lang = listen()
            def_lang = def_lang.replace("loki", "")
            talk(f"You've requested {mode} songs in {def_lang}.")
            talk("Now playing...")
            pywhatkit.playonyt(mode + " " + def_lang)
            return "Finished playing."
        if "no" in comment or "not play" in comment or "don't play" in comment:
            talk(
                "If you don't need my recommendation song, I can play a song of your choice. Please say 'yes' to proceed or 'no' to exit.")
            comment = listen()
            if 'yes' in comment or 's' in comment:
                talk("Please provide song information: the song name or song author you want.")
                song_name = listen()
                talk("Please specify the language you prefer.")
                song_language = listen()
                talk(f"You've requested {song_name} songs in {song_language}.")
                talk("Now playing...")
                pywhatkit.playonyt(song_name + " songs " + song_language)
            else:
                talk("No song selected. Exiting.")
                talk("Goodbye.")
                return "Goodbye."
    talk("Invalid input.")
    return "Invalid input."


default_language = "English"
talk("I am loki, your Music bot.")
if emotion_pred == "happy":
    text = "I think you're feeling elated. Can I play a song to add to the fun?"
elif emotion_pred == "sad":
    text = "I understand you're in pain right now. Can I play a song for you? Let's share this moment and experience it together."
elif emotion_pred == "angry":
    text = "I sense you're feeling quite frustrated. Would you like me to play a song to spend some time together and have some fun?"
else:
    text = "Your energy feels neutral. Let's add some color. Can I play a song to have fun together and make it vibrant like a beautiful rainbow?"

talk(text)

result = lokiBot(emotion_pred, default_language)
print(result)

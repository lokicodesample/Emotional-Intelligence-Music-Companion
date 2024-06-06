import cv2
import numpy as np
import pyttsx3
import speech_recognition as sr
import pywhatkit
import os
import pygame
from keras.models import model_from_json
import time
import pytube
from pydub import AudioSegment
from youtube_search import YoutubeSearch
import asyncio

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


# Initialize speech engine
speech_engine = pyttsx3.init()
speech_engine.setProperty('rate', 185)

audio_semaphore = asyncio.Semaphore(1)


# function to detect emotion
def detect_emotion():
    return final_emotion


# Function to convert text to speech
def speak(text):
    print("Emilie -> " + text)
    try:
        speech_engine.say(text)
        speech_engine.runAndWait()
    except RuntimeError as e:
        print("Error:", e)


# Function to listen to user's voice input
def record(timeout=5):
    recognizer = sr.Recognizer()
    with sr.Microphone() as mic:
        recognizer.adjust_for_ambient_noise(mic)
        recognizer.dynamic_energy_threshold = True
        print("Listening ...")
        try:
            audio = recognizer.listen(mic, timeout=timeout)
            print("Recognizing...")
            text = recognizer.recognize_google(audio, language='en-IN').lower()
            print("User -> " + text)
            return text
        except sr.UnknownValueError:
            print("Emilie -> Sorry, I couldn't understand what you said.")
        except sr.RequestError as e:
            print("Emilie -> Could not request results from Google Speech Recognition service:", e)
        except Exception as e:
            print("Error:", e)
        return ""


# function to download audio
async def download_and_convert_video(search_query):
    try:
        print("Searching for videos...")
        results = YoutubeSearch(search_query, max_results=1).to_dict()
        if results:
            video_url = "https://www.youtube.com" + results[0]['url_suffix']
            print("Downloading the audio...")
            video = pytube.YouTube(video_url)
            audio_stream = video.streams.filter(only_audio=True).first()
            audio_file = audio_stream.download()
            print("Audio downloaded successfully.")
        else:
            raise Exception("No search results found.")

        print("Converting audio to WAV format...")

        print(audio_file)
        audio = AudioSegment.from_file(audio_file)
        base = os.path.basename(audio_file)
        filename = os.path.splitext(base)[0] + ".wav"
        audio.export(filename, format="wav")
        print("Audio converted successfully.")
        return filename
    except Exception as e:
        print("Error:", e)
        return ""


# Function to stop music playback
def stop_music():
    pygame.mixer.music.stop()
    print("Music stopped.")


# Function to play music
def play_music(audio_file):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()


# Function to handle music commands
# Function to handle user commands
async def handle_user_commands(response):
    if "stop" in response:
        stop_music()
    elif "pause" in response:
        pygame.mixer.music.pause()
        speak("Music paused.")
    elif "resume" in response:
        pygame.mixer.music.unpause()
        speak("Music resumed.")
    elif "volume up" in response or "increase" in response:
        pygame.mixer.music.set_volume(min(1.0, pygame.mixer.music.get_volume() + 0.2))
        speak("Volume increased.")
    elif "volume down" in response or "decrease" in response:
        pygame.mixer.music.set_volume(max(0.0, pygame.mixer.music.get_volume() - 0.2))
        speak("Volume decreased.")
    elif "play" in response:
        response = response.replace("play", "")
        async with audio_semaphore:
            audio_file = await download_and_convert_video(response)
            play_music(audio_file)
    else:
        speak("I'm sorry, I didn't understand that command.")


# Function to listen to audio input continuously
async def listen_audio():
    try:
        while True:
            response = record()
            if response:
                if response.strip():
                    await handle_user_commands(response)
                    await asyncio.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped")


async def main():
    emotion = detect_emotion()
    lang = "english"
    try:
        if emotion == 'sad':
            speak("I sense a hint of sadness in your voice. Would you like me to play a soothing song for you?")
        elif emotion == 'happy':
            speak("You sound happy! It's great to hear that. Would you like me to play some music for you?")
        elif emotion == 'anger':
            speak("You seem upset. Would you like me to play a song to help you unwind and relax?")
        else:
            speak("Your emotion seems neutral. Would you like me to play some music for you?")
        not_handled = True
        while not_handled:
            response = record()
            if response:
                if "yes" in response:
                    not_handled = False
                    speak("Let me find some music for you")
                    async with audio_semaphore:
                        audio_file = await download_and_convert_video(emotion + "songs in " + lang)
                        if audio_file:
                            play_music(audio_file)
                elif "no" in response:
                    not_handled = False
                    speak("Do you suggest any song?")
                    no_suggestion = True
                    while no_suggestion:
                        response = record()
                        if response:
                            if "yes" in response:
                                no_suggestion = False
                                speak("which song do you want?")
                                song_not_played = True
                                while song_not_played:
                                    response = record()
                                    if response:
                                        song_not_played = False
                                        async with audio_semaphore:
                                            audio_file = await download_and_convert_video(response)
                                        play_music(audio_file)
        await asyncio.gather(listen_audio(), asyncio.sleep(0.1))
    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
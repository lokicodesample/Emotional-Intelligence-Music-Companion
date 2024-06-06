import pyttsx3
import speech_recognition as sr
import pytube
import pygame
from pydub import AudioSegment
import os
from youtube_search import YoutubeSearch
import asyncio

# Initialize speech engine
speech_engine = pyttsx3.init()
speech_engine.setProperty('rate', 185)

audio_semaphore = asyncio.Semaphore(1)

# Define the folder path where you want to save the downloaded songs
SONGS_DOWNLOAD_FOLDER = "C:\\Users\LOKESH\\PycharmProjects\\pythonProject_Music\\Songs"

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
            # Save to specific folder
            audio_file = audio_stream.download(output_path=SONGS_DOWNLOAD_FOLDER)
            print("Audio downloaded successfully.")
            print(audio_file)
        else:
            raise Exception("No search results found.")

        print("Converting audio to WAV format...")
        audio = AudioSegment.from_file(audio_file)
        base = os.path.basename(audio_file)
        filename = os.path.splitext(base)[0] + ".wav"
        # Save converted audio to the same folder
        audio.export(os.path.join(SONGS_DOWNLOAD_FOLDER, filename), format="wav")
        print("Audio converted successfully.")
        return os.path.join(SONGS_DOWNLOAD_FOLDER, filename)  # Return the full path of the converted audio file
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
    lang = "english"
    try:
        # Read the final emotion from the file
        with open('../final_emotion.txt', 'r') as f:
            emotion = f.read().strip()

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
    # Create the songs_download folder if it doesn't exist
    #if not os.path.exists(SONGS_DOWNLOAD_FOLDER):
        #os.makedirs(SONGS_DOWNLOAD_FOLDER)

    asyncio.run(main())

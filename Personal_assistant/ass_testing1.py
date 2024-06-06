import speech_recognition as sr
import pyttsx3
import pywhatkit

player = pyttsx3.init()
listener = sr.Recognizer()
emotion_pred = "sad"


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

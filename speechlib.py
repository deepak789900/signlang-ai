import speech_recognition as sr
import pyttsx3
# from gtts import gTTS  # Optional: Google Text-to-Speech
# from playsound import playsound
import os

# Initialize the recognizer
r = sr.Recognizer()

# ✅ Offline text-to-speech
def SpeakText(command):
    try:
        engine = pyttsx3.init()
        engine.say(command)
        engine.runAndWait()
    except Exception as e:
        print("Speech synthesis error:", e)

# 🔁 Optional: Google TTS (if internet is available)
def googleSpeak(command):
    from gtts import gTTS
    tts = gTTS(command)
    tts.save('test.mp3')
    os.system('start test.mp3')  # or use playsound('test.mp3')

# 🎤 Speech to Text
def speech_text():
    print("Listening...")
    try:
        with sr.Microphone() as source2:
            r.adjust_for_ambient_noise(source2, duration=0.2)
            audio2 = r.listen(source2)
            MyText = r.recognize_google(audio2)
            MyText = MyText.lower()
            print('User:', MyText)
            return MyText
    except sr.RequestError as e:
        return f"API unavailable: {e}"
    except sr.UnknownValueError:
        return "Sorry, I did not understand."

# Example usage:
# SpeakText("Hello World")
# print(speech_text())

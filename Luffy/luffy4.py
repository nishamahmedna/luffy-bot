import speech_recognition as sr
import pyttsx3
import requests
import time
import os
import sys

# === CONFIGURATION ===
OPENROUTER_API_KEY = "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"
MODEL = "openai/gpt-3.5-turbo"

# === SETUP SPEECH RECOGNITION & TTS ===
recognizer = sr.Recognizer()
tts = pyttsx3.init()
tts.setProperty("rate", 180)

# === WAKE WORDS ===
WAKE_WORDS = ["hello", "hi", "hey", "luffy", "hey luffy", "hi luffy"]

# === CLEAR TERMINAL & START MESSAGE ===
os.system("clear" if os.name == "posix" else "cls")
print("Luffy is ready, say something like 'hello', 'hey Luffy', or 'hi' to activate.")

# === SPEAK FUNCTION ===
def speak(text):
    print("Luffy:", text)
    tts.say(text)
    tts.runAndWait()

# === LISTEN FUNCTION ===
def listen(prompt="Listening..."):
    print(prompt)
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=None, phrase_time_limit=10)
    try:
        query = recognizer.recognize_google(audio)
        print("You:", query)
        return query.lower()
    except sr.UnknownValueError:
        print("Didn't catch that.")
        return ""
    except sr.RequestError:
        print("Network error.")
        return ""

# === FETCH RESPONSE FROM OPENROUTER ===
def get_openrouter_reply(question):
    print("Fetching response...")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "LuffyBot"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": question}]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

# === MAIN LOOP ===
while True:
    try:
        text = listen("Waiting for wake word...")
        if "exit" in text:
            print("Exiting...")
            sys.exit(0)

        if any(wake in text for wake in WAKE_WORDS):
            speak("What would you like to ask?")
            question = listen("Waiting for question...")

            if "stop" in question:
                print("Question cancelled.")
                continue

            if question.strip() == "":
                speak("I didn’t catch any question.")
                continue

            answer = get_openrouter_reply(question)
            print("AI:", answer)

            if "stop" not in question:
                speak(answer)

    except KeyboardInterrupt:
        print("\nStopped by user.")
        break


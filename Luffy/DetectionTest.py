import os
import sys
import time
import socket
import speech_recognition as sr
import pyttsx3
import requests

# --- Configuration ---
OPENROUTER_API_KEY = "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""  # Replace with your OpenRouter API key
MODEL = "openai/gpt-3.5-turbo"
WAKE_WORDS = ["hello", "hi", "hey", "luffy", "hey luffy", "hi luffy"]

# --- Function: Check Internet Connection ---
def is_connected(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False

# --- Wait for Internet Connection ---
print("Checking internet connection...")
while not is_connected():
    print("Waiting for internet...")
    time.sleep(2)
print("Internet connected.")

# --- Setup TTS with explicit espeak driver ---
engine = pyttsx3.init(driverName='espeak')
engine.setProperty("rate", 175)
engine.setProperty("volume", 1.0)

def speak(text):
    print("Luffy:", text)
    engine.say(text)
    engine.runAndWait()

# --- Announce Voice Confirmation ---
speak("Luffy is ready and connected to the internet.")

# --- Setup Speech Recognition ---
recognizer = sr.Recognizer()

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
        print("Network error during speech recognition.")
        return ""

# --- Fetch Response from OpenRouter ---
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

# --- Main Loop ---
print("Say something like 'hello', 'hey luffy', or 'hi' to activate.")
while True:
    try:
        text = listen("Waiting for wake word...")
        if "exit" in text:
            speak("Goodbye!")
            sys.exit(0)
        # Check if any wake word is present in the captured text
        if any(wake in text for wake in WAKE_WORDS):
            speak("What would you like to ask?")
            question = listen("Waiting for question...")
            if "stop" in question:
                speak("Okay, cancelled.")
                continue
            if not question.strip():
                speak("I didn't catch any question.")
                continue
            answer = get_openrouter_reply(question)
            print("AI:", answer)
            if "stop" not in question:
                speak(answer)
    except KeyboardInterrupt:
        print("\nStopped by user.")
        break

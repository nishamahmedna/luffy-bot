# voice_input.py

import speech_recognition as sr
import time

recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen_for_wake_word():
    print("[Voice] Listening for wake word...")
    while True:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, phrase_time_limit=3)
                command = recognizer.recognize_google(audio).lower()
                print(f"[Heard] {command}")
                if "hello" in command:
                    return "hello"
                elif "exit" in command:
                    return "exit"
        except sr.UnknownValueError:
            continue
        except Exception as e:
            print(f"[Wake Word Error] {e}")
            continue

def listen_for_question():
    print("Luffy: What would you like to ask?")
    time.sleep(0.5)
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
    try:
        question = recognizer.recognize_google(audio)
        print(f"[Question] {question}")
        return question
    except sr.UnknownValueError:
        return "I couldn't understand your question."
    except Exception as e:
        print(f"[Question Error] {e}")
        return "An error occurred while listening."

# main.py

from detection import run_detection
from voice_input import listen_for_wake_word, listen_for_question
from ai_response import get_gemini_response
from tts_output import speak
import threading
import cv2

active_mode = False

def start_bot():
    global active_mode

    # Start detection in a separate thread
    detection_thread = threading.Thread(target=run_detection, daemon=True)
    detection_thread.start()

    print("Luffy is ready. Say 'hello' to begin.")

    while True:
        command = listen_for_wake_word()

        if command == "hello":
            print("[Luffy] What would you like to ask?")
            speak("What would you like to ask?")
            active_mode = True

            question = listen_for_question()
            if question:
                print(f"You asked: {question}")
                answer = get_gemini_response(question)
                print(f"Luffy: {answer}")
                speak(answer)

        elif command == "stop":
            print("[Luffy] Stopping response and resuming detection.")
            speak("Okay, resuming detection.")
            active_mode = False

        elif command == "exit":
            print("[Luffy] Exiting the system.")
            speak("Goodbye.")
            cv2.destroyAllWindows()
            break

if __name__ == "__main__":
    start_bot()

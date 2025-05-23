
import cv2
import pytesseract
import time
import torch
import numpy as np
import speech_recognition as sr
import pyttsx3
from picamera2 import Picamera2
from threading import Thread
import queue
import signal
import sys
import google.generativeai as genai

# Initialize Gemini AI
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-pro")

# Initialize TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 170)

# Initialize speech recognizer
recognizer = sr.Recognizer()
mic = sr.Microphone()

# Load YOLOv8n model
model_yolo = torch.hub.load('ultralytics/yolov5', 'yolov5n', pretrained=True)
model_yolo.conf = 0.4

# Setup camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()
time.sleep(2)

# For stopping the assistant
running = True
paused = False

# Text detection memory
detected_texts_memory = []

# Speech queue
speech_queue = queue.Queue()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen_for_wake_word():
    global paused, running
    while running:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
                said = recognizer.recognize_google(audio).lower()
                print("Heard:", said)
                if "hello" in said:
                    paused = True
                    speak("What would you like to ask?")
                    with mic as source:
                        recognizer.adjust_for_ambient_noise(source)
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        query = recognizer.recognize_google(audio)
                        print("You asked:", query)
                        response = model.generate_content(query)
                        if hasattr(response, 'text'):
                            answer = response.text
                        else:
                            answer = "Sorry, I couldn't understand the question."
                        print("AI:", answer)
                        speak(answer)
                        paused = False

                elif "stop" in said:
                    engine.stop()
                    paused = False

                elif "exit" in said:
                    speak("Shutting down.")
                    running = False
                    sys.exit(0)
        except Exception as e:
            print("Listening error:", e)
            continue

# Start listener thread
listener_thread = Thread(target=listen_for_wake_word, daemon=True)
listener_thread.start()

# Main loop
while running:
    if paused:
        time.sleep(1)
        continue

    try:
        frame = picam2.capture_array()

        # Object Detection
        results = model_yolo(frame)
        labels, cords = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        n = len(labels)
        for i in range(n):
            row = cords[i]
            if row[4] >= 0.4:
                x1, y1, x2, y2 = int(row[0]*640), int(row[1]*480), int(row[2]*640), int(row[3]*480)
                cls = int(labels[i])
                label = model_yolo.names[cls]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

        # Text Detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        texts = pytesseract.image_to_string(gray).strip().split("\n")
        texts = [t for t in texts if t.strip()]
        if texts:
            detected_texts_memory = texts[-10:]

        y_offset = 20
        for i, text in enumerate(detected_texts_memory, start=1):
            cv2.putText(frame, f"Text {i}: {text}", (10, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            y_offset += 20

        # Show frame
        cv2.imshow("Luffy AI Bot", frame)
        if cv2.waitKey(1) == 27:
            break

    except Exception as e:
        print(f"Error: {e}")
        break

cv2.destroyAllWindows()
picam2.close()

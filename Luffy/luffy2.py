import cv2
import pytesseract
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import threading
import time
from ultralytics import YOLO

# Initialize Text-to-Speech
engine = pyttsx3.init()
engine_lock = threading.Lock()
stop_flag = False
speaking = False
luffy_awake = False
waiting_for_question = False  # Ensures only one active speech recognition
frame_frozen = False
freeze_frame = None

detected_texts = []
detected_objects = []

genai.configure(api_key="AIzaSyBBsBiYmkvedU2CaEzGlDZWiuhByULUVJA")  # Replace with actual API key
model = YOLO("yolov8n.pt")  # Load YOLOv8 model

recognizer = sr.Recognizer()
cap = cv2.VideoCapture(0)
time.sleep(2)  # Camera warm-up

def speak(text):
    """Speak asynchronously and allow interruption."""
    global speaking
    def run():
        global speaking
        with engine_lock:
            speaking = True
            engine.say(text)
            engine.runAndWait()
            speaking = False
    stop_speaking()
    threading.Thread(target=run, daemon=True).start()

def stop_speaking():
    """Stop speaking immediately."""
    global speaking
    with engine_lock:
        speaking = False
        engine.stop()

def get_gemini_response(text):
    """Fetch AI response."""
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(text)
        return response.text if response else "I couldn't find relevant information."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def listen_for_commands():
    """Continuously listen for 'hello', 'stop', or 'exit'."""
    global luffy_awake, stop_flag, frame_frozen, waiting_for_question
    while not stop_flag:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)  # Improved sensitivity
            try:
                if waiting_for_question:  # Avoid command listening during question processing
                    continue

                print("🎤 Listening for 'hello', 'stop', or 'exit'...")
                audio = recognizer.listen(source, timeout=3)
                speech_text = recognizer.recognize_google(audio).lower()
                print(f"🔊 Heard: {speech_text}")
                
                if "hello" in speech_text:
                    stop_speaking()
                    luffy_awake = True
                    frame_freeze()
                    print("🤖 Luffy: Hello! What would you like to ask?")
                    speak("Hello! What would you like to ask?")
                    time.sleep(1)  # Ensure Luffy's voice finishes before listening
                    process_speech()  # Ask the question
                
                elif "stop" in speech_text:
                    frame_unfreeze()

                elif "exit" in speech_text:
                    print("👋 Exiting Luffy...")
                    stop_flag = True
                    stop_speaking()
                    cap.release()
                    cv2.destroyAllWindows()
                    return
            except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
                continue

def process_speech():
    """Process user questions after 'hello' is detected."""
    global waiting_for_question
    if waiting_for_question:
        return  # Prevent multiple speech threads
    waiting_for_question = True
    
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            print("🎤 Listening for your question...")
            audio = recognizer.listen(source, timeout=6, phrase_time_limit=6)  # Reduced max timeout to 6s
            user_question = recognizer.recognize_google(audio).lower()
            print(f"🔊 Heard: {user_question}")
            
            ai_response = get_gemini_response(user_question)
            print(f"🤖 Luffy: {ai_response}")
            speak(ai_response)
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            speak("Can you please repeat the question?")
    
    waiting_for_question = False
    frame_unfreeze()

def frame_freeze():
    """Freeze the frame."""
    global frame_frozen
    frame_frozen = True

def frame_unfreeze():
    """Unfreeze the frame."""
    global frame_frozen
    frame_frozen = False

threading.Thread(target=listen_for_commands, daemon=True).start()

while not stop_flag:
    ret, frame = cap.read()
    if not ret or stop_flag:
        break
    
    if frame_frozen:
        if freeze_frame is not None:
            cv2.imshow("Luffy Camera", freeze_frame)
        if cv2.waitKey(1) == 27:
            stop_flag = True
            stop_speaking()
            break
        continue  # Skip further processing while frozen
    
    frame_skip = 0
    frame_skip += 1
    if frame_skip % 2 == 0:
        continue  # Reduce processing load
    
    # Detect text
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    new_texts = pytesseract.image_to_string(gray).strip().split('\n')
    detected_texts = [text for text in new_texts if text]
    
    # Detect objects
    detected_objects.clear()
    results = model(frame)
    for idx, result in enumerate(results):
        for box in result.boxes:
            class_id = int(box.cls[0])
            object_name = model.names[class_id]
            detected_objects.append(object_name)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"Object {idx+1}: {object_name}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Display detected texts
    y_offset = 30
    for i, text in enumerate(detected_texts, start=1):
        cv2.putText(frame, f"Text {i}: {text}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        y_offset += 20
    
    freeze_frame = frame.copy()
    cv2.imshow("Luffy Camera", frame)
    if cv2.waitKey(1) == 27:
        stop_flag = True
        stop_speaking()
        break

cap.release()
cv2.destroyAllWindows()



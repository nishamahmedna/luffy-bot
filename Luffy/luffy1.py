import cv2
import pytesseract
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import threading
import time
from ultralytics import YOLO  

# Initialize Components
engine = pyttsx3.init()
engine_lock = threading.Lock()
stop_flag = False
speaking = False
luffy_awake = False
processing_speech = False

detected_texts = []  
detected_objects = []  

genai.configure(api_key="AIzaSyBBsBiYmkvedU2CaEzGlDZWiuhByULUVJA")  
model = YOLO("yolov8n.pt")  

recognizer = sr.Recognizer()
mic = sr.Microphone()

cap = cv2.VideoCapture(0)
time.sleep(2)  

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
    """Continuously listen for 'hello' or 'stop'."""
    global luffy_awake, stop_flag, speaking
    while not stop_flag:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                print("🎤 Listening for 'hello' or 'stop'...")
                audio = recognizer.listen(source, timeout=3)
                speech_text = recognizer.recognize_google(audio).lower()
                print(f"🔊 Heard: {speech_text}")
                if "hello" in speech_text:
                    stop_speaking()
                    luffy_awake = True
                    print("🤖 Luffy: Hello! What would you like to ask?")
                    speak("Hello! What would you like to ask?")
                    threading.Thread(target=process_speech, daemon=True).start()
                elif "stop" in speech_text:
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
    global luffy_awake, processing_speech
    if processing_speech:
        return  
    processing_speech = True
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            print("🎤 Listening for your question...")
            audio = recognizer.listen(source, timeout=5)
            user_question = recognizer.recognize_google(audio).lower()
            print(f"🔊 Heard: {user_question}")
            ai_response = "I couldn't understand the question."
            if "text" in user_question or "object" in user_question:
                words = user_question.split()
                for word in words:
                    if word.isdigit():
                        index = int(word) - 1
                        if "text" in user_question and 0 <= index < len(detected_texts):
                            query_text = detected_texts[index]
                            ai_response = get_gemini_response(f"Explain this: {query_text}")
                        elif "object" in user_question and 0 <= index < len(detected_objects):
                            query_object = detected_objects[index]
                            ai_response = get_gemini_response(f"Tell me about {query_object}")
                        else:
                            ai_response = "I couldn't find that item."
                        break
            else:
                ai_response = get_gemini_response(user_question)
            print(f"🤖 Luffy: {ai_response}")
            speak(ai_response)
        except (sr.UnknownValueError, sr.RequestError, sr.WaitTimeoutError):
            speak("I didn't catch that. Can you repeat?")
    processing_speech = False

def detect_text(frame):
    """Detect text and display it at the corner."""
    global detected_texts
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    config = "--psm 6"
    extracted_text = pytesseract.image_to_data(gray, config=config, output_type=pytesseract.Output.DICT)

    detected_texts.clear()
    for i in range(len(extracted_text['text'])):
        text = extracted_text['text'][i].strip()
        if text and extracted_text['conf'][i] > 40:  
            detected_texts.append(text)

    return frame

threading.Thread(target=listen_for_commands, daemon=True).start()

while not stop_flag:
    ret, frame = cap.read()
    if not ret or stop_flag:
        break
    frame_skip = 0
    frame_skip += 1
    if frame_skip % 2 == 0:
        continue  
    
    # Detect text
    frame = detect_text(frame)

    # Detect objects
    detected_objects.clear()
    results = model(frame)
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            object_name = model.names[class_id]
            detected_objects.append(object_name)
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{len(detected_objects)}. {object_name}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Display numbered text list in the top-left corner
    y_offset = 30
    for i, text in enumerate(detected_texts, start=1):
        cv2.putText(frame, f"Text {i}: {text}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        y_offset += 25  

    # Display numbered object list in the bottom-left corner
    y_offset = frame.shape[0] - 100
    for i, obj in enumerate(detected_objects, start=1):
        cv2.putText(frame, f"Object {i}: {obj}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        y_offset += 25  

    # Console Log
    if detected_texts:
        print("📝 Detected Texts:")
        for i, text in enumerate(detected_texts, start=1):
            print(f"{i}️⃣ {text}")
    if detected_objects:
        print("🟢 Detected Objects:")
        for i, obj in enumerate(detected_objects, start=1):
            print(f"{i}️⃣ {obj}")

    cv2.imshow("Luffy Camera", frame)
    if cv2.waitKey(1) == 27:
        stop_flag = True
        stop_speaking()
        break

cap.release()
cv2.destroyAllWindows()


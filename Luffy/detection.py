# detection.py

import cv2
import torch
import pytesseract
from picamera2 import Picamera2
from ultralytics import YOLO
import time

# Load YOLOv8n model
model = YOLO("models/yolov8n.pt")

# Initialize PiCamera2
picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()
time.sleep(2)

# Memory for detected texts
detected_texts = []

# Detection function (runs in a separate thread)
def run_detection():
    global detected_texts

    while True:
        try:
            # Capture frame
            frame = picam2.capture_array()

            # --- Object Detection ---
            results = model(frame, verbose=False)[0]
            for box in results.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = model.names[int(box.cls[0])]
                conf = float(box.conf[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # --- Text Detection ---
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            texts = pytesseract.image_to_string(gray).strip().split("\n")
            texts = [t for t in texts if t.strip()]

            if texts:
                detected_texts = texts[-10:]
                with open("logs/detected_texts.txt", "w") as f:
                    for line in detected_texts:
                        f.write(line + "\n")

            # Display text at top left
            y_offset = 30
            for i, text in enumerate(detected_texts, start=1):
                cv2.putText(frame, f"Text {i}: {text}", (10, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                y_offset += 20

            # Show camera feed
            cv2.imshow("Luffy Live Feed", frame)
            if cv2.waitKey(1) == 27:  # ESC to quit
                break

        except Exception as e:
            print(f"[Detection Error] {e}")
            break

    cv2.destroyAllWindows()
    picam2.close()

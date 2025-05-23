import cv2
import pyttsx3
import time
import os

# Load class labels from coco.names
classNames = []
with open('coco.names', 'r') as f:
    classNames = f.read().rstrip('\n').split('\n')

# Load the pre-trained model
net = cv2.dnn_DetectionModel('frozen_inference_graph.pb', 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt')
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
spoken_label = ""  # To track the last spoken object
last_spoken_time = 0  # To control speaking frequency
speak_delay = 3  # seconds between speaking the same object

# Start video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect objects in the frame
    classIds, confidences, boxes = net.detect(frame, confThreshold=0.5)

    if len(classIds) > 0:
        # Find the object with the highest confidence
        max_conf_index = confidences.argmax()
        classId = classIds.flatten()[max_conf_index]
        confidence = confidences.flatten()[max_conf_index]
        box = boxes[max_conf_index]

        # Label and bounding box
        label = f"{classNames[classId - 1]}: {round(confidence * 100, 2)}%"
        cv2.rectangle(frame, box, color=(0, 255, 0), thickness=2)
        cv2.putText(frame, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Speak label if it's different and cooldown passed
        current_label = classNames[classId - 1]
        current_time = time.time()
        if current_label != spoken_label or (current_time - last_spoken_time) > speak_delay:
            engine.say(current_label)
            engine.runAndWait()
            spoken_label = current_label
            last_spoken_time = current_time

    cv2.imshow("Object Detection with Audio", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release everything
cap.release()
cv2.destroyAllWindows()
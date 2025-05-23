import cv2
import numpy as np
from picamera2 import Picamera2

net = cv2.dnn.readNet("models/yolov3-tiny.weights", "models/yolov3-tiny.cfg")
with open("models/coco.names", "r") as f:
	classes = [line.strip() for line in f.readlines()]
	
layer_names = net.getUnconnectedOutLayersNames()

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

while True:
	frame = picam2.capture_array()
	height, width, _ = frame.shape
	
	blob =cv2.dnn.blobFromImage(frame, 1/255, (416,416), swapRB=True, crop=False)
	net.setInput(blob)
	outputs = net.forward(layer_names)
	
	boxes = []
	confidences = []
	class_id = []
	
	for output in outputs:
		for detection in output:
			scores = detection[5:]
			class_id = int(scores.argmax())
			confidence = scores[class_id]
			
			if confidence > 0.5:
				center_x = int(detection[0] * width)
				center_y = int (detection[1] * height)
				w = int(detection[2] * width)
				h = int(detection[3] * height)
				x = int(center_x - w / 2)
				y =  int(center_y - h / 2)
				
				boxes.append([x,y,w,h])
				confidences.append(float(confidence))
				class_ids.append(class_id)
				
		indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
		
	if len(indexes) > 0:
		for i in indexes:
			i = i[0] if isintance(i, (list, tuple, np.ndarray)) else i
			x, y, w, h = boxes[i]
			label = str(classes[class_ids[i]])
			confidence = str(round(confidences[i], 2))
			
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 266, 0), 2)
			cv2.putText(frrame, label + "" + confidence, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)	
		cv2.imshow("YOLO object dewtection", frame)
		
		if cv2.waitKey(1) & 0xFF == 27:
			break
			
picam2.stop()
cv2.destroyAllWindows()	
				 
				
				
			
			
			
			
			
			

from picamera2 import Picamera2
import cv2
import pytesseract

cap = cv2.VideoCapture(0)
cv2.waitKey(1000)

while True:
	ret, frame = cap.read()
	if not ret:
		print("failed to grab")
		break
		
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
	
	custom_config = r'--oem 3 --psm 6'
	text = pytesseract.image_to_string(processed, config = custom_config)
	
	lines = text.strip().split('\n')
	y = 20
	for i, line in enumerate(lines):
		if line.strip() != "":
			cv2.putText(frame, f"Text {i+1}: {line}", (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
			y += 20
			
	cv2.imshow("text", frame)
	
	if cv2.waitKey(1) & 0xFF == 27:
		break

cap.release()
cv2.destroyAllWindows()


from picamera2 import Picamera2
import cv2
import time

picam2 = Picamera2()
picam2.preview_configuration.main.size = (640, 480)
picam2.preview_configuration.main.format = "RGB888"
picam2.preview_configuration.align()
picam2.configure("preview")
picam2.start()
time.sleep(2)

while True:
    try:
        frame = picam2.capture_array()
        cv2.imshow("live camera feed", frame)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break
    except Exception as e:
        print(f"error capturing: {e}")
        break
            
cv2.destroyAllWindows()
picam2.close()


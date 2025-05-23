from picamera2 import Picamera2
import time

# Initialize camera
picam2 = Picamera2()

# Configure preview mode
picam2.preview_configuration.main.size = (1280, 720)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")

# Start camera
picam2.start()
time.sleep(2)  # Allow camera to warm up

# Capture and save image
picam2.capture_file("image.jpg")
print("Image saved as image.jpg")

picam2.stop()
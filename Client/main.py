"""
This is the client main.py file this python script was designed to capture images using PiCamera2, 
detect cars in the captured images, and draw bounding boxes around detected cars. 
It interfaces with a FastAPI server that processes the image and returns the detection results. 
The script continuously captures images at a defined interval, submits them to the FastAPI 
server for car detection, and saves the annotated images (Does not save them with drawn boxes for some reason).

Key functionalities include:
- Capturing images at regular intervals.
- Sending the captured images to a FastAPI server for car detection.
- Receiving car detection data, including bounding boxes, from the server.
- Annotating the captured images with bounding boxes around detected cars.
- Saving the annotated images with a timestamp in their filenames.

The script also handles termination requests, ensuring that the PiCamera2 is 
properly stopped before exiting.

To use this script, ensure that the FastAPI server's external IP address and port are correctly specified in the 
`base_URI` variable. The FastAPI server should provide an endpoint for car detection (`/detectCar/`) that accepts 
image files and returns detection data.

Note: This script requires the PiCamera2 library for capturing images and PIL (Python Imaging Library) 
for image processing and drawing.

Python requirements:
install needed libraries ( located in requirements.txt)
"""

import requests
from PIL import Image, ImageDraw
from picamera2 import Picamera2
from datetime import datetime
import time
import signal
import sys

# Replace with the external IP address of your VM where FastAPI is running
base_URI = 'http://34.171.180.221:8080/'

def detect_and_draw_cars(filename):
    with open(filename, 'rb') as f:
        files = {'uploaded_file': f}
        response = requests.post(base_URI + 'detectCar/', files=files)
        if response.status_code != 200:
            print("Error during car detection:", response.text)
            return
        cars_response = response.json().get('cars', {})
        if not cars_response:
            print("No cars detected.")
            return
            
        image = Image.open(filename)
        drawing = ImageDraw.Draw(image)
        
        for car, details in cars_response.items():
            bounding_box = details.get('box', [])
            if bounding_box:
                drawing.rectangle(bounding_box, outline="red")
        save_filename = f"cars_detected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        image.save(save_filename)
        print("Cars detected and saved to", save_filename)

def capture_image(picam2):
    print("Capturing a new image...")
    filename = f'capture_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
    picam2.start_and_capture_file(filename)
    print(f"Image captured and saved as {filename}")
    detect_and_draw_cars(filename)

def signal_handler(sig, frame):
    print('Turning off camera and exiting...')
    picam2.stop()
    sys.exit(0)

if __name__ == "__main__":
    picam2 = Picamera2()
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        capture_image(picam2)
        time.sleep(10)

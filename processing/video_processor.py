import os
import cv2
import math
from ultralytics import YOLO
import cvzone
from dotenv import load_dotenv
from twilio.rest import Client
from email_notification import send_email_alert 
import time

load_dotenv()

# Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_from_number = os.getenv("TWILIO_FROM_NUMBER")
twilio_to_number = os.getenv("TWILIO_TO_NUMBER")

client = Client(account_sid, auth_token)

# Define message threshold and time interval
message_threshold = 20
notification_interval = 60  # in seconds

# Initialize frame_counter, last_notification_time, and accident_notification_sent flag
frame_counter = 0
last_notification_time = 0
accident_notification_sent = False

def send_sms_alert():
    message = client.messages.create(
        body='Accident detected! Please check and respond.And reach at the location of https://maps.app.goo.gl/RveMLfBfugVg1P8k6',
        from_=twilio_from_number,
        to=twilio_to_number
    )
    print(f"Twilio message SID: {message.sid}")

def detect_accident(video_file):
    global frame_counter, last_notification_time, accident_notification_sent

    model = YOLO('yolov.pt')
    cap = cv2.VideoCapture(video_file)
    accident_detected = False

    while True:
        # Read frame from video capture
        success, img = cap.read()
        if not success:
            break
        
        # Perform object detection
        results = model(img, stream=True)

        # Iterate over detection results
        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1

                conf = math.ceil((box.conf[0] * 100)) / 100    
                label = 'ACCIDENT'
                cvzone.cornerRect(img, (x1, y1, w, h))
                cvzone.putTextRect(img, f'{label} {conf}', (max(0, x1), max(35, y1)), colorR=(0, 165, 255))
                
                # Check if accident is detected and message has not been sent yet
                if not accident_notification_sent:
                    accident_detected = True
                    print("Accident detected in video frame.")
                    
                    # Check if enough time has passed since the last notification
                    current_time = time.time()
                    if current_time - last_notification_time >= notification_interval:
                        # Send email alert
                        send_email_alert()
                        # Send SMS alert
                        send_sms_alert()
                        last_notification_time = current_time  # Update last notification time
                        accident_notification_sent = True
                
        # Increment frame counter
        frame_counter += 1

        # Reset frame counter and accident_notification_sent flag if message_threshold frames have passed
        if frame_counter >= message_threshold:
            frame_counter = 0
            accident_notification_sent = False
        
        # Encode frame to JPEG format
        _, jpeg = cv2.imencode('.jpg', img)
        frame_data = jpeg.tobytes()

        # Yield processed frame and accident detected flag
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n'), accident_detected

    cap.release()

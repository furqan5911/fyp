import cv2
import math
import time
import cvzone
import os
from ultralytics import YOLO
from dotenv import load_dotenv
from twilio.rest import Client
from email_notification import send_email_alert  # Assuming you have defined this function in email_notification.py

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

# Initialize accident_message_sent flag
accident_message_sent = False
last_notification_time = 0

def send_sms_alert():
    message = client.messages.create(
        body='Accident detected! Please check and respond.',
        from_=twilio_from_number,
        to=twilio_to_number
    )
    print(f"Twilio message SID: {message.sid}")

def detect_accident(frame):
    global accident_message_sent, last_notification_time

    model = YOLO('yolov8s.pt')

    # Perform object detection
    results = model(frame, stream=True)
    accident_detected = False

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1

            conf = math.ceil((box.conf[0] * 100)) / 100    
            label = 'ACCIDENT'
            cvzone.cornerRect(frame, (x1, y1, w, h))
            cvzone.putTextRect(frame, f'{label} {conf}', (max(0, x1), max(35, y1)), colorR=(0, 165, 255))
            
            if not accident_message_sent:
                accident_detected = True
                print("Accident detected in webcam frame.")
                
                # Check if enough time has passed since the last notification
                current_time = time.time()
                if current_time - last_notification_time >= notification_interval:
                    # Send email alert
                    send_email_alert()
                    # Send SMS alert
                    send_sms_alert()
                    last_notification_time = current_time  # Update last notification time
                    accident_message_sent = True

    # Encode frame to JPEG format
    _, buffer = cv2.imencode('.jpg', frame)
    frame_data = buffer.tobytes()

    return (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n'), accident_detected

def generate_frames():
    cap = cv2.VideoCapture(0)  # Capture video from the default webcam

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Detect accident and yield frame
        frame, accident_detected = detect_accident(frame)
        
        # Reset accident_message_sent flag if accident is not detected
        if not accident_detected:
            global accident_message_sent
            accident_message_sent = False

        yield frame

    cap.release()


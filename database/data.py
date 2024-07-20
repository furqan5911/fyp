from database.models import db, Accident
from flask import current_app
from datetime import datetime
import pytz

def handle_accident_detection(sender, app):
    print("Signal received: Handling accident detection")
    try:
        with app.app_context():
            print("Inside app context: Adding accident record to database")
            # Generate timestamp in UTC timezone
            # Get the timezone for Pakistan
            pakistan_timezone = pytz.timezone('Asia/Karachi')
            utc_now = datetime.now(pakistan_timezone)
            new_accident = Accident(timestamp=utc_now)
            db.session.add(new_accident)
            db.session.commit()
            print("Accident record saved to database")
    except Exception as e:
        print(f"Error saving accident record: {e}")


from flask import Flask, render_template, request, redirect, url_for, Response, session
from processing.video_processor import detect_accident
from processing.web import generate_frames  # Import the function from web.py
from auth.login import login_user, logout_user
from database.models import db, Accident
from database.data import handle_accident_detection
import os

app = Flask(__name__)

# Generate your secret key using os.urandom(24).hex()
app.secret_key = '78fba490a7879c2d836b661b5d4b8272c867b06b9011d517'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Absolute path to avoid confusion
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(BASE_DIR, 'instance', 'accidents.db')

# Ensure the instance directory exists
if not os.path.exists(os.path.join(BASE_DIR, 'instance')):
    os.makedirs(os.path.join(BASE_DIR, 'instance'))

# Check if the database file exists
if not os.path.exists(database_path):
    open(database_path, 'w').close()  # Create an empty file

# Configure SQLAlchemy database URI
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Add this line to disable a warning
db.init_app(app)

# Pagination settings
PER_PAGE = 10

def format_timestamp(timestamp, format_type):
    if format_type == 'year':
        return timestamp.year
    elif format_type == 'month':
        return timestamp.month
    elif format_type == 'day':
        return timestamp.day
    elif format_type == 'hour':
        return timestamp.hour
    elif format_type == 'minute':
        return timestamp.minute

@app.context_processor
def utility_processor():
    return {
        'format_timestamp': format_timestamp,
    }

@app.route("/", methods=["GET", "POST"])
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("home.html")

@app.route("/upload", methods=["GET", "POST"])
def upload_video():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == "POST":
        if 'file' not in request.files:
            return "No file part"

        file = request.files.get('file')

        if not file or file.filename == '':
            return "No selected file"

        if file:
            # Save the uploaded video file
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(video_path)

            # Redirect to video display page
            return redirect(url_for('display_video', video_file=file.filename))

    return render_template("upload.html")

@app.route("/webcam")
def webcam():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("webcam.html")

@app.route("/webcam_feed")
def webcam_feed():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/display/<video_file>")
def display_video(video_file):
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    return render_template("video.html", video_file=video_file)

@app.route("/predict", methods=["POST"])
def predict():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    video_file = request.form.get("video_file")
    if not video_file:
        return "No video file specified"

    video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_file)

    def generate():
        for frame, accident_detected in detect_accident(video_path):
            yield frame
            if accident_detected:
                print("Calling handle_accident_detection function.")
                with app.app_context():
                    handle_accident_detection(sender=app, app=app)

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/login", methods=["GET", "POST"])
def login():
    return login_user()

@app.route("/logout")
def logout():
    session.clear()  # Clear session data on logout
    return redirect(url_for('login'))  # Redirect to the login page after logout

@app.route("/view_records")
def view_records():
    page = request.args.get('page', 1, type=int)
    records = Accident.query.paginate(page=page, per_page=PER_PAGE)
    return render_template("view_records.html", records=records.items, page=page, total_pages=records.pages)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
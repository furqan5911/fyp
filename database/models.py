from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Accident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
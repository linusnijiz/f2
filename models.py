from database import db
from datetime import datetime
import uuid

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(200))
    plan = db.Column(db.String(20), default="free")
    last_click = db.Column(db.DateTime, default=datetime(2000, 1, 1))
    balance = db.Column(db.Float, default=0.0)
    referral_code = db.Column(db.String(50), unique=True, default=lambda: str(uuid.uuid4())[:8])
    referred_by = db.Column(db.String(50), nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(200), nullable=True)
    followers_sent = db.Column(db.Integer, default=0)


class Referral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referrer = db.Column(db.Integer)
    new_user = db.Column(db.Integer)

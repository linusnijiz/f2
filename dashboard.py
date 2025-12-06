from flask import Blueprint, render_template, request, session, jsonify
from models import User
from database import db
import requests
from datetime import datetime
import config

dash_bp = Blueprint("dash", __name__)

from flask import Blueprint, render_template, session, redirect
from models import User
from database import db
from config import PLAN_SETTINGS
from datetime import datetime

dash_bp = Blueprint("dashboard", __name__)

@dash_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])

    # PLAN-DATEN LADEN
    plan_data = PLAN_SETTINGS[user.plan]

    # COOLDOWN BERECHNEN
    now = datetime.utcnow()
    elapsed = (now - user.last_click).total_seconds()
    cooldown = plan_data["cooldown"]
    remaining = max(0, int(cooldown - elapsed))

    # AFFILIATE → Geworbene Nutzer
    referred_users = User.query.filter_by(referred_by=user.referral_code).all()

    # Für das Dashboard: generierter Umsatz (falls du das nutzt)
    total_generated = sum([u.balance for u in referred_users])

    # Gesamtanzahl Aktionen (falls noch nicht implementiert → 0)
    total_actions = 0

    return render_template(
        "dashboard.html",
        user=user,
        plan_data=plan_data,
        remaining=remaining,
        referred_users=referred_users,
        total_generated=total_generated,
        total_actions=total_actions,
        plan_settings=PLAN_SETTINGS  # 🔥 WICHTIG FÜR DEIN HTML
    )




@dash_bp.route("/send_order", methods=["POST"])
def send_order():
    # 1. Check login
    if "user_id" not in session:
        return jsonify({"error": "Nicht eingeloggt!"}), 401

    user = User.query.get(session["user_id"])
    if not user:
        return jsonify({"error": "User nicht gefunden!"}), 404

    # 2. Hole Plan-Daten
    plan_data = config.PLAN_SETTINGS[user.plan]

    now = datetime.utcnow()
    diff = (now - user.last_click).total_seconds()

    # 3. Cooldown Prüfung
    if diff < plan_data["cooldown"]:
        remaining = int(plan_data["cooldown"] - diff)
        return jsonify({"error": f"Cooldown aktiv! Bitte {remaining} Sekunden warten."}), 429

    # 4. JSON prüfen
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Ungültige Anfrage (kein JSON)!"}), 400

    link = data.get("link")
    if not link:
        return jsonify({"error": "Bitte einen Link angeben!"}), 400

    # 5. Auftrag an API
    payload = {
        "key": config.FASTER_API_KEY,
        "action": "add",
        "service": str(config.FASTER_SERVICE_ID),
        "link": link,
        "quantity": plan_data["quantity"]
    }

    try:
        response = requests.post(config.FASTER_API_URL, data=payload)
        api_result = response.json()
    except Exception as e:
        return jsonify({"error": f"API Fehler: {str(e)}"}), 500

    # API Fehler prüfen
    if "error" in api_result:
        return jsonify({"error": api_result["error"]}), 400

    # 6. Cooldown setzen
    user.last_click = now

    # 🚀 7. FOLLOWER GESAMT ERHÖHEN (NEU)
    user.followers_sent += plan_data["quantity"]

    db.session.commit()

    # 8. Erfolg an Frontend zurückgeben
    return jsonify({
        "success": True,
        "message": "Follower gesendet!",
        "followers_added": plan_data["quantity"],
        "followers_total": user.followers_sent
    })





from flask import redirect

@dash_bp.before_request
def check_login():
    if "user_id" not in session:
        return redirect("/login")

from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Referral
from database import db

auth_bp = Blueprint("auth", __name__)

from mail import send_mail
import uuid

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        existing = User.query.filter_by(email=email).first()

        # 1️⃣ Fall: E-Mail existiert bereits
        if existing:

            # Aber E-Mail ist NICHT bestätigt
            if not existing.email_verified:

                # neuen Token erzeugen
                token = str(uuid.uuid4())
                existing.reset_token = token
                db.session.commit()

                verify_link = f"http://127.0.0.1:5000/verify?token={token}"

                send_mail(
                    email,
                    "Bitte bestätige deine Registrierung erneut",
                    f"Du hattest bereits ein Konto registriert.\n"
                    f"Bitte bestätige deine E-Mail über diesen Link:\n\n{verify_link}"
                )

                return render_template("email_sent.html")

            # 2️⃣ Wenn E-Mail bereits existiert und VERIFIZIERT ist:
            return render_template("register.html", error="Diese E-Mail existiert bereits!")

        # 3️⃣ Neuer User – alles normal
        token = str(uuid.uuid4())

        new_user = User(
            email=email,
            username=username,
            password=password,
            referral_code=str(uuid.uuid4())[:8],
            email_verified=False,
            reset_token=token
        )

        db.session.add(new_user)
        db.session.commit()

        verify_link = f"http://127.0.0.1:5000/verify?token={token}"

        send_mail(
            email,
            "Bitte bestätige deine Registrierung",
            f"Klicke auf den Link, um deinen Account zu bestätigen:\n\n{verify_link}"
        )

        return render_template("email_sent.html")

    return render_template("register.html")




@auth_bp.route("/verify")
def verify():
    token = request.args.get("token")

    user = User.query.filter_by(reset_token=token).first()

    if not user:
        return "Ungültiger Link"

    user.email_verified = True
    user.reset_token = None
    db.session.commit()

    return render_template("verify_success.html")

@auth_bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()

        if not user:
            return "Diese E-Mail existiert nicht."

        token = str(uuid.uuid4())
        user.reset_token = token
        db.session.commit()

        reset_link = f"http://127.0.0.1:5000/reset?token={token}"

        send_mail(
            user.email,
            "Passwort zurücksetzen",
            f"Klicke auf den Link, um dein Passwort zurückzusetzen:\n\n{reset_link}"
        )

        return "E-Mail zum Passwort-Reset wurde gesendet!"

    return render_template("forgot.html")

@auth_bp.route("/reset", methods=["GET", "POST"])
def reset():
    token = request.args.get("token")
    user = User.query.filter_by(reset_token=token).first()

    # ❌ Token ungültig
    if not user:
        return render_template("reset.html", error="Ungültiger oder abgelaufener Link.")

    # POST: Neues Passwort speichern
    if request.method == "POST":
        new_pw = request.form.get("new_password")

        # Validierung (optional)
        if len(new_pw) < 6:
            return render_template("reset.html", error="Das Passwort muss mindestens 6 Zeichen enthalten.")

        # Passwort speichern
        user.password = generate_password_hash(new_pw)
        user.reset_token = None
        db.session.commit()

        # ✔ Erfolgsmeldung anzeigen
        return render_template("reset.html", success="Passwort erfolgreich geändert!")

    # GET: Seite anzeigen
    return render_template("reset.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        pw = request.form["password"]

        user = User.query.filter_by(email=email).first()

        # ❌ Email existiert nicht
        if not user:
            return render_template("login.html", error="Diese E-Mail ist nicht registriert.")

        # ❌ Email existiert, aber Passwort falsch
        if not check_password_hash(user.password, pw):
            return render_template("login.html", error="Das Passwort ist falsch.")

        # ❌ Benutzer hat E-Mail noch nicht bestätigt
        if not user.email_verified:
            return render_template("login.html", error="Bitte bestätige zuerst deine E-Mail.")

        # ✔ Login erfolgreich
        session["user_id"] = user.id
        return redirect("/dashboard")

    # GET: Einfach Login-Seite anzeigen
    return render_template("login.html")



@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


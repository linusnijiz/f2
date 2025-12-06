from flask import Flask, render_template   # ⬅️ render_template hinzufügen
from database import db
import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    # MODELLE LADEN
    from models import User, Referral

    # Tabellen erzeugen
    with app.app_context():
        print("📌 Creating database tables...")
        db.create_all()

    # Blueprints registrieren
    from auth import auth_bp
    from dashboard import dash_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)

    return app


app = create_app()

# ⭐ STARTSEITE EINBAUEN ⭐
@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)

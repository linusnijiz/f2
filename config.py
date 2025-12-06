SECRET_KEY = "DEIN_SECRET"
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"

FASTER_API_KEY = "8f013f1d493e2fcae0106669f38d9a78"
FASTER_SERVICE_ID = 11106
FASTER_API_URL = "https://fastersmm.com/api/v2"

PLAN_SETTINGS = {
    "free": {
        "cooldown": 1800,   # 30 min
        "quantity": 100
    },
    "paid1": {
        "cooldown": 10,    # 10 min
        "quantity": 100
    },
    "paid2": {
        "cooldown": 120,    # 2 min
        "quantity": 1000
    }
}

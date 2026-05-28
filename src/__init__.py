from flask import Flask
from src.views.api_routes import api_bp
from pathlib import Path
import os

db_config = {
    "host" : os.getenv("DB_HOST"),
    "database" : os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT")),
    "user" : os.getenv("DB_USER"),
    "password" : os.getenv("DB_PASSWORD")
}

conn_pool = None 

def create_app():
    app = Flask(__name__, static_folder=Path(__file__).parents[1] / "static")
    app.register_blueprint(api_bp)
    return app

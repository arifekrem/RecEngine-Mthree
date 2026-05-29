from flask import Flask
from src.views.api_routes import api_bp
from pathlib import Path

conn_pool = None 

def create_app():
    app = Flask(__name__, static_folder=Path(__file__).parents[1] / "static")
    app.register_blueprint(api_bp)
    return app

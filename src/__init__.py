from flask import Flask
from src.models.db_pool import init_connection_pool
from src.views.api_routes import api_bp


db_config = {
    "host" : '127.0.0.1',
    "database" : 'reconciliation_db',
    "port": 3306,
    "user" : 'rec_user',
    "password" : 'xkir23'
}

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    conn_pool = init_connection_pool(db_config)
    return app
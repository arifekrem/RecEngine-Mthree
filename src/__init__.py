import logging

from flask import Flask, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.observability.metrics import refresh_db_gauges
from src.views.api_routes import api_bp
from pathlib import Path

logger = logging.getLogger(__name__)

conn_pool = None


def create_app():
    app = Flask(__name__, static_folder=Path(__file__).parents[1] / "static")
    app.register_blueprint(api_bp)

    @app.route("/metrics")
    def metrics():
        try:
            refresh_db_gauges()
        except Exception:
            logger.exception("Could not refresh DB gauges; exporting counters only")
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

    return app

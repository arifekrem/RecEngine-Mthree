from flask import Blueprint

api_bp = Blueprint('api', __name__)

@api_bp.route("/")
def home():
    return "<h1>Welcome to the lab</h1>"
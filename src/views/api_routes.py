from flask import Blueprint, jsonify, request, Response
from src.models.transaction_db import ping_connection
from src.models.transaction_db import fetch_transaction_table_dict

api_bp = Blueprint('api', __name__)

@api_bp.route("/")
def home():
    return "<h1>Welcome to the lab</h1>"

@api_bp.route("/test_fetching_table_transaction")
def test_transaction_table_fetch():
    table_dict = fetch_transaction_table_dict("transactions")
    return jsonify(table_dict), 200

@api_bp.route("/test_fetching_table_other")
def test_other_table_fetch():
    table_dict = fetch_transaction_table_dict("processor_records")
    return jsonify(table_dict), 200
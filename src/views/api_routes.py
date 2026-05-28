from flask import Blueprint, jsonify, request, Response, render_template
from src.models.transaction_db import _fetch_table_records, insert_transaction, delete_transaction, update_transaction
from src.controllers.simulate import run_simulation
from src.controllers.reconcile import run_reconciliation_process
from pathlib import Path

api_bp = Blueprint('api', __name__, static_folder = Path(__file__).parents[2] / "static")

@api_bp.route("/index")
def home():
    return api_bp.send_static_file("index.html")

@api_bp.route("/transactions")
def transactions_route():
    return api_bp.send_static_file("transactions.html")

@api_bp.route("/reconciliation")
def reconciliation_route():
    return api_bp.send_static_file("reconciliation.html")

"""@api_bp.route("/transactions")
def test_transactions_fetch():
    table_dict = _fetch_table_records("transactions")
    return jsonify(table_dict), 200"""


@api_bp.route("/processor_records")
def test_processors_fetch():
    table_dict = _fetch_table_records("processor_records")
    return jsonify(table_dict), 200

@api_bp.route("/card_network_records")
def test_cards_fetch():
    table_dict = _fetch_table_records("card_network_records")
    return jsonify(table_dict), 200

@api_bp.route("/bank_transaction_records")
def test_banks_fetch():
    table_dict = _fetch_table_records("bank_transaction_records")
    return jsonify(table_dict), 200



@api_bp.route("/reconciliation_runs")
def test_reconciliation_runs():
    simulation_batch = _fetch_table_records("reconciliation_runs")

    return jsonify(simulation_batch), 200

@api_bp.route("/reconciliation_results")
def test_reconciliation_results():
    simulation_batch = _fetch_table_records("reconciliation_results")

    return jsonify(simulation_batch), 200



@api_bp.route("/run_simulation")
def test_simulation_run():
    simulation_batch = run_simulation()

    return jsonify(simulation_batch), 200

@api_bp.route("/run_reconciliation")
def test_reconciliation_run():
    simulation_batch = run_reconciliation_process()

    return jsonify(simulation_batch), 200


@api_bp.route("/transactions_data")
def transactions_data():

    table_dict = _fetch_table_records("transactions")

    return jsonify(table_dict), 200

@api_bp.route("/add_transaction", methods=["POST"])
def add_transaction():
    data = request.get_json()

    transaction_id = insert_transaction(
        data["customer_id"],
        data["business_id"],
        data["amount"],
        data["received_at"]
    )

    return jsonify({
        "message": "Transaction added successfully",
        "transaction_id": transaction_id
    }), 201

@api_bp.route("/delete_transaction/<int:transaction_id>", methods=["DELETE"])
def delete_transaction_route(transaction_id):
    rows_deleted = delete_transaction(transaction_id)

    return jsonify({
        "message": "Transaction deleted successfully",
        "rows_deleted": rows_deleted
    }), 200

@api_bp.route("/update_transaction/<int:transaction_id>", methods=["PUT"])
def update_transaction_route(transaction_id):
    data = request.get_json()

    rows_updated = update_transaction(
        transaction_id,
        data["customer_id"],
        data["business_id"],
        data["amount"],
        data["received_at"]
    )

    return jsonify({
        "message": "Transaction updated successfully",
        "rows_updated": rows_updated
    }), 200
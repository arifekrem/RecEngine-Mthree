from flask import Blueprint, jsonify, request, Response, render_template
from src.models.transaction_db import fetch_table_records
from src.controllers.simulate import run_simulation
from src.controllers.reconcile import run_reconciliation_process
from pathlib import Path

api_bp = Blueprint('api', __name__, static_folder = Path(__file__).parents[2] / "static")

# Index page
@api_bp.route("/index")
def home():
    return api_bp.send_static_file("index.html")

@api_bp.route("/api/display_recent_reconciliation_results")
def get_dashboard_results_table():
    return fetch_table_records("reconciliation_results")


# Reconciliation page
@api_bp.route("/reconciliation")
def reconciliation_route():
    return api_bp.send_static_file("reconciliation.html")

@api_bp.route("/api/run_reconciliation")
def run_reconciliation():
    run_reconciliation_process()
    return fetch_table_records("reconciliation_results")

@api_bp.route("/api/display_reconciliation_results")
def get_reconciliation_results_table():
    return fetch_table_records("reconciliation_results")


# Transactions page
@api_bp.route("/transactions")
def test_transactions_fetch():
    return api_bp.send_static_file("transactions.html")

@api_bp.route("/api/display_transactions")
def get_transactions_results_table():
    return fetch_table_records("reconciliation_results")



@api_bp.route("/processor_records")
def test_processors_fetch():
    table_dict = fetch_table_records("processor_records")
    return jsonify(table_dict), 200

@api_bp.route("/card_network_records")
def test_cards_fetch():
    table_dict = fetch_table_records("card_network_records")
    return jsonify(table_dict), 200

@api_bp.route("/bank_transaction_records")
def test_banks_fetch():
    table_dict = fetch_table_records("bank_transaction_records")
    return jsonify(table_dict), 200



@api_bp.route("/reconciliation_runs")
def test_reconciliation_runs():
    simulation_batch = fetch_table_records("reconciliation_runs")

    return jsonify(simulation_batch), 200

@api_bp.route("/reconciliation_results")
def test_reconciliation_results():
    simulation_batch = fetch_table_records("reconciliation_results")

    return jsonify(simulation_batch), 200



@api_bp.route("/run_simulation")
def test_simulation_run():
    simulation_batch = run_simulation()

    return jsonify(simulation_batch), 200

@api_bp.route("/run_reconciliation")
def test_reconciliation_run():
    simulation_batch = run_reconciliation_process()

    return jsonify(simulation_batch), 200

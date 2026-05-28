from flask import Blueprint, jsonify, request, Response
from src.models.transaction_db import _fetch_table_records
from src.controllers.simulate import run_simulation
from src.controllers.reconcile import run_reconciliation_process

api_bp = Blueprint('api', __name__)

@api_bp.route("/")
def home():
    return "<h1>Welcome to the lab</h1>"

@api_bp.route("/transactions")
def test_transactions_fetch():
    table_dict = _fetch_table_records("transactions")
    return jsonify(table_dict), 200

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

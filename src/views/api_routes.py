from flask import Blueprint, jsonify, request, redirect
from src.models.transaction_db import (
    TransactionPipelineError,
    fetch_table_records,
    get_transaction_pipeline,
    insert_transaction,
    delete_transaction,
    update_transaction,
)
from src.controllers.simulate import run_simulation
from src.controllers.reconcile import run_reconciliation_process
from pathlib import Path

api_bp = Blueprint('api', __name__, static_folder = Path(__file__).parents[2] / "static")

# Index page
@api_bp.route("/")
def root():
    return redirect("/index")

@api_bp.route("/index")
def home():
    return api_bp.send_static_file("index.html")

@api_bp.route("/api/reconciliation_results")
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

@api_bp.route("/api/reconciliation_results")
def get_reconciliation_results_table():
    return fetch_table_records("reconciliation_results")


# Transactions page
@api_bp.route("/transactions")
def transaction_route():
    return api_bp.send_static_file("transactions.html")

@api_bp.route("/api/display_transactions")
def get_transactions_results_table():
    try:
        return fetch_table_records("transactions")
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@api_bp.route("/add_transaction", methods=["POST"])
def add_transaction():
    data = request.get_json(silent=True) or {}
    required_fields = ("customer_id", "business_id", "amount", "received_at")
    missing = [
        field for field in required_fields
        if field not in data or data[field] in (None, "")
    ]
    if missing:
        return jsonify({
            "error": "Missing required fields",
            "missing_fields": missing,
        }), 400

    try:
        result = insert_transaction(
            data["customer_id"],
            data["business_id"],
            data["amount"],
            data["received_at"],
        )
    except TransactionPipelineError as exc:
        return jsonify({
            "error": str(exc),
            "failed_stage": exc.stage,
            "transaction_id": exc.transaction_id,
            "message": f"Transaction pipeline failed at stage: {exc.stage}",
        }), 422
    except Exception as exc:
        return jsonify({
            "error": str(exc),
            "message": "Unexpected error while creating transaction",
        }), 500

    return jsonify({
        "message": "Transaction processed through all pipeline stages",
        "transaction_id": result["transaction_id"],
        "stages": result["stages"],
    }), 201


@api_bp.route("/transaction_pipeline/<int:transaction_id>")
def transaction_pipeline_status(transaction_id):
    pipeline = get_transaction_pipeline(transaction_id)
    if not pipeline.get("found"):
        return jsonify({
            "error": "Transaction not found",
            "transaction_id": transaction_id,
        }), 404
    return jsonify(pipeline), 200

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


    """ test routes """

@api_bp.route("/run_simulation")
def test_simulation_run():
    simulation_batch = run_simulation()
    return jsonify(simulation_batch), 200

@api_bp.route("/transaction_table")
def test1():
    return fetch_table_records("transactions")

@api_bp.route("/processor_records_table")
def test2():
    return fetch_table_records("processor_records")

@api_bp.route("/card_network_records_table")
def test3():
    return fetch_table_records("card_network_records")

@api_bp.route("/bank_transaction_records_table")
def test4():
    return fetch_table_records("bank_transaction_records")

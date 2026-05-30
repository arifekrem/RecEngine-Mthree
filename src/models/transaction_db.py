from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional, Union

from src.observability.metrics import (
    record_pipeline_failure,
    record_simulation_batch,
    record_transaction_created,
    record_transaction_deleted,
)

from .db_pool import get_db_connection

logger = logging.getLogger(__name__)


class TransactionPipelineError(Exception):
    """Raised when transaction processing fails at a named pipeline stage."""

    def __init__(
        self,
        stage: str,
        message: str,
        transaction_id: Optional[int] = None,
    ) -> None:
        self.stage = stage
        self.transaction_id = transaction_id
        super().__init__(message)

ALLOWED_TABLES = {
    "transactions",
    "processor_records",
    "card_network_records",
    "bank_transaction_records"
}


NETWORK_NAMES = ("Visa", "Mastercard", "SWIFT")
BANK_NAMES = ("Citi", "Chase", "Bank of America", "Wells Fargo")
def generate_simulation_batch(
    total_records: int = 100,
    chaos_ratio: float = 0.15,
    seed: Optional[int] = None,
) -> Dict[str, int]:
    """
    Insert simulated transactions and downstream records.

    Good records are consistent across all tables.
    Chaos records intentionally include one mismatch pattern:
    - MissingDownstream
    - AmountMismatch
    - StatusMismatch
    - OrderMismatch
    """
    if total_records <= 0:
        raise ValueError("total_records must be greater than 0")
    if not 0 <= chaos_ratio <= 1:
        raise ValueError("chaos_ratio must be between 0 and 1")

    rng = random.Random(seed)
    connection = get_db_connection()
    cursor = connection.cursor()

    counters = {
        "total": total_records,
        "good": 0,
        "chaos": 0,
        "missing_downstream": 0,
        "amount_mismatch": 0,
        "status_mismatch": 0,
        "order_mismatch": 0,
    }

    base_time = datetime.utcnow() - timedelta(minutes=5)

    try:
        for idx in range(total_records):
            tx_time = base_time + timedelta(seconds=idx * 2)
            amount = round(rng.uniform(5.00, 3000.00), 4)
            customer_id = rng.randint(1000, 9000)
            business_id = rng.randint(1, 400)

            transaction_id = _insert_transaction(
                cursor=cursor,
                customer_id=customer_id,
                business_id=business_id,
                amount=amount,
                received_at=tx_time,
            )

            is_chaos = rng.random() < chaos_ratio
            if not is_chaos:
                _insert_happy_path(cursor, transaction_id, tx_time, amount, rng)
                counters["good"] += 1
                continue

            anomaly = rng.choice(
                ("MissingDownstream", "AmountMismatch", "StatusMismatch", "OrderMismatch")
            )
            _insert_chaos_path(cursor, transaction_id, tx_time, amount, anomaly, rng)
            counters["chaos"] += 1

            if anomaly == "MissingDownstream":
                counters["missing_downstream"] += 1
            elif anomaly == "AmountMismatch":
                counters["amount_mismatch"] += 1
            elif anomaly == "StatusMismatch":
                counters["status_mismatch"] += 1
            else:
                counters["order_mismatch"] += 1

        connection.commit()
        record_simulation_batch(counters)
        return counters
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()
        
def _json_safe_row(row: Dict[str, Any]) -> Dict[str, Any]:
    safe: Dict[str, Any] = {}
    for key, value in row.items():
        if isinstance(value, datetime):
            safe[key] = value.isoformat(sep=" ")
        elif isinstance(value, Decimal):
            safe[key] = float(value)
        else:
            safe[key] = value
    return safe


def fetch_table_records(table_name):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary = True)
        
        # No sql injections because table name is whitelisted, and col_str is not accessible by users.
        cursor.execute(f"SELECT * FROM {table_name}") 
        table_data = cursor.fetchall()
        return [_json_safe_row(row) for row in table_data]
    finally:
        cursor.close()
        connection.close()


def _insert_transaction(cursor, customer_id: int, business_id: int, amount: float, received_at: datetime) -> int:
    cursor.execute(
        """
        INSERT INTO transactions (customer_id, business_id, amount, received_at)
        VALUES (%s, %s, %s, %s)
        """,
        (customer_id, business_id, amount, received_at),
    )
    return int(cursor.lastrowid)


def _coerce_datetime(value: Union[datetime, str]) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    raise TypeError(f"received_at must be datetime or str, got {type(value).__name__}")


def _propagate_transaction_pipeline(
    cursor,
    transaction_id: int,
    tx_time: datetime,
    amount: float,
    *,
    status: str = "Success",
    network_name: Optional[str] = None,
    bank_name: Optional[str] = None,
    rng: Optional[random.Random] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Stages 2–4: processor → card network → bank.
    Returns metadata for each downstream stage (for API responses and logging).
    """
    processor_time = tx_time + timedelta(seconds=1)
    network_time = processor_time + timedelta(seconds=1)
    bank_time = network_time + timedelta(seconds=1)

    pick_rng = rng or random.Random()
    network = network_name or pick_rng.choice(NETWORK_NAMES)
    bank = bank_name or pick_rng.choice(BANK_NAMES)

    stages: Dict[str, Dict[str, Any]] = {}

    try:
        processor_record_id = _insert_processor_record(
            cursor, transaction_id, status, processor_time
        )
        stages["processor_record"] = {
            "status": "ok",
            "processor_record_id": processor_record_id,
            "record_status": status,
            "received_at": processor_time.isoformat(sep=" "),
        }
        logger.info(
            "Stage 2 complete: processor_record_id=%s transaction_id=%s",
            processor_record_id,
            transaction_id,
        )
    except Exception as exc:
        raise TransactionPipelineError(
            "processor_record",
            f"Failed to create processor record: {exc}",
            transaction_id,
        ) from exc

    try:
        card_network_record_id = _insert_card_network_record(
            cursor, transaction_id, network, status, network_time
        )
        stages["card_network_record"] = {
            "status": "ok",
            "card_network_record_id": card_network_record_id,
            "network_name": network,
            "record_status": status,
            "received_at": network_time.isoformat(sep=" "),
        }
        logger.info(
            "Stage 3 complete: card_network_record_id=%s transaction_id=%s",
            card_network_record_id,
            transaction_id,
        )
    except Exception as exc:
        raise TransactionPipelineError(
            "card_network_record",
            f"Failed to create card network record: {exc}",
            transaction_id,
        ) from exc

    try:
        bank_record_id = _insert_bank_record(
            cursor, transaction_id, bank, status, bank_time, amount
        )
        stages["bank_record"] = {
            "status": "ok",
            "bank_record_id": bank_record_id,
            "bank_name": bank,
            "record_status": status,
            "received_at": bank_time.isoformat(sep=" "),
            "amount": float(amount),
        }
        logger.info(
            "Stage 4 complete: bank_record_id=%s transaction_id=%s",
            bank_record_id,
            transaction_id,
        )
    except Exception as exc:
        raise TransactionPipelineError(
            "bank_record",
            f"Failed to create bank record: {exc}",
            transaction_id,
        ) from exc

    return stages


def _insert_happy_path(cursor, transaction_id: int, tx_time: datetime, amount: float, rng: random.Random) -> None:
    _propagate_transaction_pipeline(
        cursor,
        transaction_id,
        tx_time,
        amount,
        status="Success",
        rng=rng,
    )


def _insert_chaos_path(
    cursor,
    transaction_id: int,
    tx_time: datetime,
    amount: float,
    anomaly: str,
    rng: random.Random,
) -> None:
    processor_time = tx_time + timedelta(seconds=1)
    network_time = processor_time + timedelta(seconds=1)
    bank_time = network_time + timedelta(seconds=1)

    if anomaly == "MissingDownstream":
        _insert_processor_record(cursor, transaction_id, "Success", processor_time)
        return

    if anomaly == "AmountMismatch":
        _insert_processor_record(cursor, transaction_id, "Success", processor_time)
        _insert_card_network_record(
            cursor, transaction_id, rng.choice(NETWORK_NAMES), "Success", network_time
        )
        mismatch_amount = round(amount + rng.uniform(0.50, 35.00), 4)
        _insert_bank_record(
            cursor,
            transaction_id,
            rng.choice(BANK_NAMES),
            "Success",
            bank_time,
            mismatch_amount,
        )
        return

    if anomaly == "StatusMismatch":
        _insert_processor_record(cursor, transaction_id, "Success", processor_time)
        _insert_card_network_record(
            cursor, transaction_id, rng.choice(NETWORK_NAMES), "Failed", network_time
        )
        _insert_bank_record(
            cursor, transaction_id, rng.choice(BANK_NAMES), "Success", bank_time, amount
        )
        return

    # OrderMismatch
    _insert_processor_record(cursor, transaction_id, "Success", processor_time)
    _insert_card_network_record(
        cursor, transaction_id, rng.choice(NETWORK_NAMES), "Success", network_time
    )
    _insert_bank_record(
        cursor,
        transaction_id,
        rng.choice(BANK_NAMES),
        "Success",
        tx_time - timedelta(seconds=1),  # Deliberately earlier than upstream steps.
        amount,
    )


def _insert_processor_record(cursor, transaction_id: int, status: str, received_at: datetime) -> int:
    cursor.execute(
        """
        INSERT INTO processor_records (transaction_id, status, received_at)
        VALUES (%s, %s, %s)
        """,
        (transaction_id, status, received_at),
    )
    return int(cursor.lastrowid)


def _insert_card_network_record(
    cursor,
    transaction_id: int,
    network_name: str,
    status: str,
    received_at: datetime,
) -> int:
    cursor.execute(
        """
        INSERT INTO card_network_records
        (network_name, transaction_id, status, received_at)
        VALUES (%s, %s, %s, %s)
        """,
        (network_name, transaction_id, status, received_at),
    )
    return int(cursor.lastrowid)


def _insert_bank_record(
    cursor,
    transaction_id: int,
    bank_name: str,
    status: str,
    received_at: datetime,
    amount: float,
) -> int:
    cursor.execute(
        """
        INSERT INTO bank_transaction_records
        (transaction_id, bank_name, status, received_at, amount)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (transaction_id, bank_name, status, received_at, amount),
    )
    return int(cursor.lastrowid)

def insert_transaction(customer_id, business_id, amount, received_at) -> Dict[str, Any]:
    """
    Create a transaction and propagate it through all four pipeline stages
    in a single database transaction (all-or-nothing).
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    transaction_id: Optional[int] = None
    stages: Dict[str, Dict[str, Any]] = {}

    try:
        tx_time = _coerce_datetime(received_at)
        amount_value = float(amount)

        try:
            transaction_id = _insert_transaction(
                cursor,
                int(customer_id),
                int(business_id),
                amount_value,
                tx_time,
            )
        except Exception as exc:
            raise TransactionPipelineError(
                "transaction_created",
                f"Failed to create transaction: {exc}",
            ) from exc

        stages["transaction_created"] = {
            "status": "ok",
            "transaction_id": transaction_id,
            "customer_id": int(customer_id),
            "business_id": int(business_id),
            "amount": amount_value,
            "received_at": tx_time.isoformat(sep=" "),
        }
        logger.info("Stage 1 complete: transaction_id=%s", transaction_id)

        downstream_stages = _propagate_transaction_pipeline(
            cursor,
            transaction_id,
            tx_time,
            amount_value,
            status="Success",
        )
        stages.update(downstream_stages)

        connection.commit()
        record_transaction_created()
        logger.info(
            "Transaction pipeline complete for transaction_id=%s", transaction_id
        )
        return {"transaction_id": transaction_id, "stages": stages}
    except TransactionPipelineError as exc:
        connection.rollback()
        record_pipeline_failure(exc.stage)
        logger.exception(
            "Transaction pipeline failed at stage (transaction_id=%s)",
            transaction_id,
        )
        raise
    except Exception as exc:
        connection.rollback()
        logger.exception("Unexpected error during transaction pipeline")
        raise TransactionPipelineError(
            "transaction_created",
            f"Unexpected pipeline error: {exc}",
            transaction_id,
        ) from exc
    finally:
        cursor.close()
        connection.close()


def get_transaction_pipeline(transaction_id: int) -> Dict[str, Any]:
    """Fetch a transaction and its downstream records for observability."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM transactions WHERE transaction_id = %s",
            (transaction_id,),
        )
        transaction = cursor.fetchone()
        if not transaction:
            return {"found": False, "transaction_id": transaction_id}

        cursor.execute(
            "SELECT * FROM processor_records WHERE transaction_id = %s",
            (transaction_id,),
        )
        processor_records = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM card_network_records WHERE transaction_id = %s",
            (transaction_id,),
        )
        card_network_records = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM bank_transaction_records WHERE transaction_id = %s",
            (transaction_id,),
        )
        bank_records = cursor.fetchall()

        return {
            "found": True,
            "transaction_id": transaction_id,
            "transaction": transaction,
            "processor_records": processor_records,
            "card_network_records": card_network_records,
            "bank_transaction_records": bank_records,
            "pipeline_complete": bool(
                processor_records and card_network_records and bank_records
            ),
        }
    finally:
        cursor.close()
        connection.close()


def delete_transaction(transaction_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM transactions WHERE transaction_id = %s",
            (transaction_id,)
        )

        connection.commit()
        rows_deleted = cursor.rowcount
        if rows_deleted:
            record_transaction_deleted()
        return rows_deleted

    finally:
        cursor.close()
        connection.close()

def update_transaction(transaction_id, customer_id, business_id, amount, received_at):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE transactions
            SET customer_id = %s,
                business_id = %s,
                amount = %s,
                received_at = %s
            WHERE transaction_id = %s
            """,
            (customer_id, business_id, amount, received_at, transaction_id)
        )

        connection.commit()

        return cursor.rowcount

    finally:
        cursor.close()
        connection.close()

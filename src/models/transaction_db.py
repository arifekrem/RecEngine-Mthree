from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Dict, Optional

from src.models.db_pool import get_db_connection


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
    chaos_target = int(round(total_records * chaos_ratio))

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

            is_chaos = idx < chaos_target
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
        return counters
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def _insert_transaction(cursor, customer_id: int, business_id: int, amount: float, received_at: datetime) -> int:
    cursor.execute(
        """
        INSERT INTO transactions (customer_id, buisness_id, amount, received_at)
        VALUES (%s, %s, %s, %s)
        """,
        (customer_id, business_id, amount, received_at),
    )
    return int(cursor.lastrowid)


def _insert_happy_path(cursor, transaction_id: int, tx_time: datetime, amount: float, rng: random.Random) -> None:
    processor_time = tx_time + timedelta(seconds=1)
    network_time = processor_time + timedelta(seconds=1)
    bank_time = network_time + timedelta(seconds=1)

    _insert_processor_record(cursor, transaction_id, "Success", processor_time)
    _insert_card_network_record(
        cursor, transaction_id, rng.choice(NETWORK_NAMES), "Success", network_time
    )
    _insert_bank_record(
        cursor, transaction_id, rng.choice(BANK_NAMES), "Success", bank_time, amount
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


def _insert_processor_record(cursor, transaction_id: int, status: str, received_at: datetime) -> None:
    cursor.execute(
        """
        INSERT INTO processor_records (processor_record_id, transaction_id, status, received_at)
        VALUES (%s, %s, %s, %s)
        """,
        (transaction_id, transaction_id, status, received_at),
    )


def _insert_card_network_record(
    cursor,
    transaction_id: int,
    network_name: str,
    status: str,
    received_at: datetime,
) -> None:
    cursor.execute(
        """
        INSERT INTO card_network_records
        (card_network_record_id, network_name, transaction_id, status, received_at)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (transaction_id, network_name, transaction_id, status, received_at),
    )


def _insert_bank_record(
    cursor,
    transaction_id: int,
    bank_name: str,
    status: str,
    received_at: datetime,
    amount: float,
) -> None:
    cursor.execute(
        """
        INSERT INTO bank_transaction_records
        (bank_record_id, transaction_id, bank_name, status, received_at, amount)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (transaction_id, transaction_id, bank_name, status, received_at, amount),
    )

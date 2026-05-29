from __future__ import annotations

import logging
from typing import Dict

from prometheus_client import Counter, Gauge

logger = logging.getLogger(__name__)

TRANSACTIONS_CREATED = Counter(
    "recengine_transactions_created_total",
    "Transactions successfully created through the full pipeline.",
)
TRANSACTIONS_DELETED = Counter(
    "recengine_transactions_deleted_total",
    "Transactions deleted from the ledger.",
)
PIPELINE_FAILURES = Counter(
    "recengine_pipeline_failures_total",
    "Transaction pipeline failures by stage.",
    ["stage"],
)
SIMULATION_BATCHES = Counter(
    "recengine_simulation_batches_total",
    "Simulation batch runs completed.",
)
SIMULATION_TRANSACTIONS = Counter(
    "recengine_simulation_transactions_total",
    "Transactions inserted by simulation.",
    ["kind"],
)
RECONCILIATION_RUNS = Counter(
    "recengine_reconciliation_runs_total",
    "Reconciliation batch runs completed.",
)
RECONCILIATION_LAST_RECORDS_CHECKED = Gauge(
    "recengine_reconciliation_last_records_checked",
    "Records checked in the most recent reconciliation run.",
)
RECONCILIATION_LAST_MISMATCHES = Gauge(
    "recengine_reconciliation_last_mismatches",
    "Mismatches found in the most recent reconciliation run.",
)

TRANSACTIONS_IN_DB = Gauge(
    "recengine_transactions_in_database",
    "Current row count in the transactions table.",
)
PROCESSOR_RECORDS_IN_DB = Gauge(
    "recengine_processor_records_in_database",
    "Current row count in processor_records.",
)
RECONCILIATION_RESULTS_BY_STATUS = Gauge(
    "recengine_reconciliation_results_by_status",
    "Current reconciliation_results rows grouped by status.",
    ["status"],
)

_RECON_STATUSES = (
    "Match",
    "MissingDownstream",
    "AmountMismatch",
    "StatusMismatch",
    "OrderMismatch",
)


def record_transaction_created() -> None:
    TRANSACTIONS_CREATED.inc()


def record_transaction_deleted() -> None:
    TRANSACTIONS_DELETED.inc()


def record_pipeline_failure(stage: str) -> None:
    PIPELINE_FAILURES.labels(stage=stage or "unknown").inc()


def record_simulation_batch(counters: Dict[str, int]) -> None:
    SIMULATION_BATCHES.inc()
    SIMULATION_TRANSACTIONS.labels(kind="good").inc(counters.get("good", 0))
    SIMULATION_TRANSACTIONS.labels(kind="chaos").inc(counters.get("chaos", 0))


def record_reconciliation_run(records_checked: int, num_mismatches: int) -> None:
    RECONCILIATION_RUNS.inc()
    RECONCILIATION_LAST_RECORDS_CHECKED.set(records_checked)
    RECONCILIATION_LAST_MISMATCHES.set(num_mismatches)


def refresh_db_gauges() -> None:
    """Refresh gauges from MySQL so Prometheus scrapes current table state."""
    from src.models.db_pool import get_db_connection

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM transactions")
        TRANSACTIONS_IN_DB.set(cursor.fetchone()[0])

        cursor.execute("SELECT COUNT(*) FROM processor_records")
        PROCESSOR_RECORDS_IN_DB.set(cursor.fetchone()[0])

        for status in _RECON_STATUSES:
            RECONCILIATION_RESULTS_BY_STATUS.labels(status=status).set(0)

        cursor.execute(
            """
            SELECT status, COUNT(*) AS cnt
            FROM reconciliation_results
            GROUP BY status
            """
        )
        for status, count in cursor.fetchall():
            RECONCILIATION_RESULTS_BY_STATUS.labels(status=status).set(count)
    except Exception:
        logger.exception("Failed to refresh DB gauges for Prometheus")
        raise
    finally:
        cursor.close()
        connection.close()

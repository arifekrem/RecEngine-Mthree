import logging

from datetime import datetime, timedelta

from src.models.discrepancy_db import (
    _insert_into_reconciliation_runs,
    _insert_into_reconciliation_results,
)
from src.observability.metrics import record_reconciliation_run

logger = logging.getLogger(__name__)


def run_reconciliation_process():
    """
    Audit run: classifies each transaction (Match, Pending, or mismatch types).
    Pending covers in-flight pipelines with incomplete downstream or Pending status.
    """
    start_time = datetime.utcnow() - timedelta(minutes=6)
    end_time = datetime.utcnow()

    run_stats = _insert_into_reconciliation_runs(start_time, end_time)
    _insert_into_reconciliation_results(run_stats["run_id"])

    records_checked = run_stats["records_checked"]
    num_mismatches = run_stats["num_mismatches"]
    record_reconciliation_run(records_checked, num_mismatches)
    logger.info(
        "Reconciliation run %s complete: records_checked=%s num_mismatches=%s",
        run_stats["run_id"],
        records_checked,
        num_mismatches,
    )
    return run_stats

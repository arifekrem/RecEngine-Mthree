from src.models.discrepancy_db import _insert_into_reconciliation_runs, _insert_into_reconciliation_results
from datetime import datetime, timedelta

def run_reconciliation_process():

    start_time = datetime.utcnow() - timedelta(minutes=6)
    end_time = datetime.utcnow()

    last_row_id = _insert_into_reconciliation_runs(start_time, end_time)
    _insert_into_reconciliation_results(last_row_id)

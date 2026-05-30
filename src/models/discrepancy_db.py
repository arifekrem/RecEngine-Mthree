from .db_pool import close_db_resources, get_db_connection

SHARED_RECON_CORE = """
    transactions t
    LEFT JOIN processor_records p ON t.transaction_id = p.transaction_id
    LEFT JOIN card_network_records c ON t.transaction_id = c.transaction_id
    LEFT JOIN bank_transaction_records b ON t.transaction_id = b.transaction_id
"""


def _insert_into_reconciliation_runs(start_time, end_time):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = f"""
        INSERT INTO reconciliation_runs (start_time, end_time, records_checked, num_mismatches)
        SELECT
            %s AS start_time,
            %s AS end_time,
            COUNT(*) AS records_checked,
            SUM(CASE
                WHEN (p.transaction_id IS NULL OR c.transaction_id IS NULL OR b.transaction_id IS NULL) OR
                t.amount <> b.amount OR
                NOT (t.received_at <= p.received_at AND p.received_at <= c.received_at AND c.received_at <= b.received_at) OR
                NOT (p.status = c.status AND c.status = b.status)
                THEN 1 ELSE 0
            END) AS num_mismatches
        FROM {SHARED_RECON_CORE};
        """
        cursor.execute(query, (start_time, end_time))
        connection.commit()
        run_id = int(cursor.lastrowid)
        cursor.execute(
            """
            SELECT records_checked, num_mismatches
            FROM reconciliation_runs
            WHERE id = %s
            """,
            (run_id,),
        )
        row = cursor.fetchone()
        return {
            "run_id": run_id,
            "records_checked": int(row[0] or 0),
            "num_mismatches": int(row[1] or 0),
        }
    finally:
        close_db_resources(connection, cursor)


def _insert_into_reconciliation_results(run_id):
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = f"""
        INSERT INTO reconciliation_results (run_id, transaction_id, status)
        SELECT
            %s AS run_id,
            t.transaction_id,
            (CASE
                WHEN p.transaction_id IS NULL OR c.transaction_id IS NULL OR b.transaction_id IS NULL
                THEN 'MissingDownstream'

                WHEN t.amount <> b.amount
                THEN 'AmountMismatch'

                WHEN NOT (
                    t.received_at <= p.received_at
                    AND p.received_at <= c.received_at
                    AND c.received_at <= b.received_at
                )
                THEN 'OrderMismatch'

                WHEN NOT (p.status = c.status AND c.status = b.status)
                THEN 'StatusMismatch'

                ELSE 'Match'
            END) AS status
        FROM {SHARED_RECON_CORE};
        """
        cursor.execute(query, (run_id,))
        connection.commit()
        return int(cursor.lastrowid)
    finally:
        close_db_resources(connection, cursor)

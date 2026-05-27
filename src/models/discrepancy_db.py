"""


FUNCTION save_reconciliation_results(discrepancy_list, matched_list):
    OPEN database connection
    START atomic transaction
    
    FOR each item in discrepancy_list:
        # e.g., INSERT INTO discrepancies (tx_id, error_type) VALUES ('TX123', 'Timestamp Sequence Violation')
        RUN SQL: INSERT into 'discrepancies' table 
        
    FOR each id in matched_list:
        # Final flag clearing the transaction records across your systems
        RUN SQL: UPDATE 'transactions' SET status = 'RECONCILED' WHERE transaction_id = id
        
    COMMIT transaction
    CLOSE connection

"""
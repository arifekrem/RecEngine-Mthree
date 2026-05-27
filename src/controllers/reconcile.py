from src.models.transaction_db import fetch_transaction_table_dict

def run_reconciliation_process():
    transactions_dict = fetch_transaction_table_dict("transactions")
    processor_dict = fetch_transaction_table_dict("processor_records")
    card_dict = fetch_transaction_table_dict("card_network_records")
    bank_dict = fetch_transaction_table_dict("bank_transaction_records")
from .db_pool import get_db_connection
ALLOWED_TABLES = {
    "transactions",
    "processor_records",
    "card_network_records",
    "bank_transaction_records"
}
def ping_connection():
    print("opening connection")
    connection = get_db_connection()
    print("closing connection")
    connection.close()

def fetch_table_records(table_name, records_col):
    if table_name not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")
    col_str = ", ".join(records_col)
    connection, cursor = None, None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT {col_str} FROM {table_name}") 
        table_data = cursor.fetchall() # a dictionary
        return table_data
    finally:
        cursor.close()
        connection.close()

def fetch_transaction_table_dict(table_name):
    if table_name == "transactions":
        return fetch_table_records(table_name, ["transaction_id", "amount", "received_at"])
    return fetch_table_records(table_name, ["transaction_id", "amount", "status", "received_at"])
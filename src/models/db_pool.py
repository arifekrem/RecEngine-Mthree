import os

import mysql.connector
from mysql.connector import pooling

# Defaults match docker-compose.yml so local/docker runs stay in sync.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "rec_user"),
    "password": os.getenv("DB_PASSWORD", "recengine"),
    "database": os.getenv("DB_NAME", "reconciliation_db"),
}

# Inits the connection pool. Not not Globally because of Docker Issues later.
conn_pool = None


def get_db_connection():
    global conn_pool

    if conn_pool is None:
        conn_pool = pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            **DB_CONFIG,
            connection_timeout=5,
        )

    return conn_pool.get_connection()


def close_db_resources(connection=None, cursor=None):
    """Safely close cursor/connection when setup may have failed mid-try."""
    if cursor is not None:
        cursor.close()
    if connection is not None:
        connection.close()

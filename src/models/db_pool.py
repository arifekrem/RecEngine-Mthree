import mysql.connector
from mysql.connector import pooling
import os

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# Inits the connection pool. Not not Globally because of Docker Issues later.
conn_pool = None
# Gets a connection from the pool lazily
def get_db_connection():
    global conn_pool

    if conn_pool is None:
        conn_pool = pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            **DB_CONFIG,
            connection_timeout=5
        )

    return conn_pool.get_connection()

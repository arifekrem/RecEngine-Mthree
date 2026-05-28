import mysql.connector
from mysql.connector import pooling

# Inits the connection pool. Not not Globally because of Docker Issues later.
conn_pool = None
# Gets a connection from the pool lazily
def get_db_connection():
    global conn_pool

    if conn_pool is None:
        conn_pool = pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            **db_config,
            connection_timeout=5
        )

    return conn_pool.get_connection()

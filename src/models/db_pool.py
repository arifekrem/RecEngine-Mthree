import mysql.connector
from mysql.connector import pooling

# Inits the connection pool. Not not Globally because of Docker Issues later.
db_connection_pool = None
def init_connection_pool(db_config):
    global db_connection_pool
    if not db_connection_pool:
        db_connection_pool = pooling.MySQLConnectionPool(
            pool_name = 'mypool',
            pool_size = 5,
            **db_config,
            connection_timeout=5
        )
    return db_connection_pool

# Gets a connection from the pool
def get_db_connection():
    global db_connection_pool
    return db_connection_pool.get_connection()
import mysql.connector

FEATURE_VARIANT = 'full'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'test',
    'allow_local_infile': True
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

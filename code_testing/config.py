import mysql.connector

FEATURE_VARIANT = 'purchase'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'test'
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

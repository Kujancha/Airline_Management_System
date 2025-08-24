# db_utils.py
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",      # Write your own username
    "password": "root",  # and password    
    "database": "dataset.sql"
}

def db_connect():
    return mysql.connector.connect(**DB_CONFIG)

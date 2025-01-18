import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def db_connect():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        with conn.cursor() as cursor:
            cursor.execute('SELECT 1')
        print("db.py: Database connection established successfully.")
        return conn
    except Exception as e:
        print(f"db.py: Error connecting to database: {e}")
        raise

def db_close(conn):
    if conn:
        conn.close()
        print("db.py: Database connection closed.")
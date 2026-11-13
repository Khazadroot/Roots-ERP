import os
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
load_dotenv()


def get_db_connection():
    try:
        connection = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME")
        )
        return connection
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return None


if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("Connection to PostgreSQL database successful")
        conn.close()

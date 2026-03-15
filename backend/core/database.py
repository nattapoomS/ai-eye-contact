import mysql.connector
from mysql.connector import Error
from core.config import settings

def get_db_connection():
    """Create and return a MySQL database connection."""
    try:
        connection = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return None

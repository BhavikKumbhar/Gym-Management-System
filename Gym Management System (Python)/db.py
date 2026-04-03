import mysql.connector

def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="gym_user",
            password="gym123",
            database="gym_management"
        )
    except Exception as e:
        print("Database connection failed:", e)
        return None

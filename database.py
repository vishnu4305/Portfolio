import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="portfolio",
        password="portfolio@123",
        database="portfolio_db"
    )
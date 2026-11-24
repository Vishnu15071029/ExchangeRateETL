import os

import pyodbc
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv("SQL_CONNECTION_STRING")

if not connection_string:
    raise ValueError("SQL_CONNECTION_STRING is missing. Check the .env file.")

connection = pyodbc.connect(connection_string, timeout=5)
cursor = connection.cursor()
cursor.execute("SELECT DB_NAME()")
database_name = cursor.fetchone()[0]

print(f"Connected to: {database_name}")
connection.close()
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv(".env")

my_sql_host = os.getenv('MY_SQL_HOST')
my_sql_user = os.getenv('MY_SQL_USER')
my_sql_password = os.getenv('MY_SQL_PASSWORD')
my_sql_schema = os.getenv('MY_SQL_SCHEMA_NAME')

mydb = mysql.connector.connect(
            host = my_sql_host,
            user = my_sql_user,
            password = my_sql_password,
            database = my_sql_schema
            )

mycursor = mydb.cursor()

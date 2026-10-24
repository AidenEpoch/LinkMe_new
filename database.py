import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

db_pool = pooling.MySQLConnectionPool(
    pool_name = "LinkMe_pool",
    pool_size = 5,
    pool_reset_session = True,
    user = os.environ["DB_USER"],
    host = os.environ["DB_HOST"],
    port=int(os.environ.get("DB_PORT", "3306")),
    password=os.environ["DB_PASSWORD"],
    database=os.environ["DB_NAME"]
)

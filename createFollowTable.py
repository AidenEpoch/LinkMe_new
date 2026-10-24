import mysql.connector

con = mysql.connector.connect(
    user = "root",
    host = "localhost",
    password = "12345",
    database = "linkme_local"
)

sql = """
    CREATE TABLE IF NOT EXISTS follow(
    follower_id BIGINT NOT NULL,
    following_id BIGINT NOT NULL,
    followe_data DATETIME NOT NULL DEFAULT CURRENT TIME_STAMP
    )
"""
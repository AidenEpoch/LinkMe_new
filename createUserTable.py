import mysql.connector

con = mysql.connector.connect(
    user = "root",
    password = "12345",
    host = "localhost", 
    database = "linkme_local"  
)

cursor = con.cursor()

sql = """
CREATE TABLE IF NOT EXISTS users(
id BIGINT PRIMARY KEY AUTO_INCREMENT NOT NULL,
user_name VARCHAR(255) NOT NULL,
email VARCHAR(255) NOT NULL,
password_hash VARCHAR(255) NOT NULL,
display_name VARCHAR(255) NOT NULL,
bio TEXT,
avatar_url VARCHAR(512) NOT NULL,
is_private BOOLEAN NOT NULL DEFAULT FALSE,
status ENUM("active", "suspended", "deleted") NOT NULL DEFAULT "active",
created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
"""

cursor.execute(sql)
con.commit()

print("已在linkme_local 中建立 users table")


from database import db_pool


sql = """
    CREATE TABLE IF NOT EXISTS clubs (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,

    name VARCHAR(256) NOT NULL,
    type VARCHAR(100),
    description TEXT,
    img_url VARCHAR(1024),

    owner_id BIGINT NOT NULL,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (owner_id) REFERENCES users(id)
);
"""
con = None
cursor = None

try:
    con = db_pool.get_connection()
    cursor = con.cursor(dictionary = True)
    cursor.execute(sql)
    con.commit()
    print(f"已經建立clubs table")
except Exception as e:
    print(f"伺服器內部錯誤: {str(e)}")
finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()
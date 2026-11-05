from database import db_pool

sql = """
    CREATE TABLE IF NOT EXISTS post_like(
        user_id BIGINT NOT NULL,
        post_id BIGINT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, post_id),
        FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE,
        FOREIGN KEY (post_id)
            REFERENCES posts(id)
            ON DELETE CASCADE,
        INDEX idx_post_id (post_id)
    )
"""

con = None
cursor = None

try:
    con = db_pool.get_connection()
    cursor = con.cursor()
    cursor.execute(sql)
    con.commit()
    print(f"已經成功建立post_like table")

except Exception as e:
    print(f"沒有順利連上伺服器: {str(e)}")

finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()
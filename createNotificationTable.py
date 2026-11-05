from database import db_pool

con = None
cursor = None

sql = """
    CREATE TABLE IF NOT EXISTS notifications(
        id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,

        user_id BIGINT NOT NULL,
        actor_id BIGINT NOT NULL,

        type VARCHAR(50) NOT NULL,

        post_id BIGINT,
        comment_id BIGINT,

        is_read BOOLEAN NOT NULL DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY (user_id) References users(id),
        FOREIGN KEY (actor_id) REFERENCES users(id),
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (comment_id) REFERENCES comments(id)
    )
"""

try:
    con = db_pool.get_connection()
    cursor = con.cursor()
    cursor.execute(sql)
    con.commit()
    print(f"成功建立 notification table")

except Exception as e:
    print(f"連線資料庫失敗: {str(e)}")

finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()

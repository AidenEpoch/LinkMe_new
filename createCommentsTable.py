from database import db_pool

con = None
cursor = None
sql = """
    CREATE TABLE IF NOT EXISTS comments(
        id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        post_id BIGINT NOT NULL,
        sender_id BIGINT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        content TEXT NOT NULL,

        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (sender_id) REFERENCES users(id),

        INDEX idx_comments_post (
            post_id,
            created_at,
            id
        )
    );
"""


try:
    con = db_pool.get_connection()
    cursor = con.cursor()
    print(f"以連線至資料庫")
    cursor.execute(sql)
    con.commit()
    print(f"已成功建立 comments table")

except Exception as e:
    print(f"無法連線至資料庫: {str(e)}")

finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()
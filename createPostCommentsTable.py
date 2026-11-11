from database import db_pool

sql = """
    CREATE TABLE IF NOT EXISTS post_comments (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_post_comments (post_id, created_at, id),

    FOREIGN KEY (post_id) REFERENCES posts(id)
        ON DELETE CASCADE,

    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);
"""

con = None
cursor = None

try:
    con = db_pool.get_connection()
    cursor = con.cursor(dictionary = True)
    cursor.execute(sql)
    con.commit()
    print(f"已經建立 post_comments table")
except Exception as e:
    print(f"無法連線至資料庫: {str(e)}")

finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()
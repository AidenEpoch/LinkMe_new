from database import db_pool

con = None
cursor = None
sql = """
    CREATE TABLE IF NOT EXISTS stores (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_store_user_post (user_id, post_id),

    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (post_id) REFERENCES posts(id)
        ON DELETE CASCADE
);
"""

try:
    con = db_pool.get_connection()
    cursor = con.cursor(dictionary = True)
    cursor.execute(sql)
    con.commit()
    print(f"已經成功建立 stores table")
except Exception as e:
    print(f"無法連線至資料庫: {str(e)}")
finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()




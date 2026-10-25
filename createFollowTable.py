from database import db_pool

sql = """
    CREATE TABLE IF NOT EXISTS follows(
        follower_id BIGINT NOT NULL,
        following_id BIGINT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

        PRIMARY KEY (follower_id, following_id),

        INDEX idx_following (following_id, follower_id),

        FOREIGN KEY (follower_id)
            REFERENCES users(id)
            ON DELETE CASCADE,

        FOREIGN KEY (following_id)
            REFERENCES users(id)
            ON DELETE CASCADE,

        CONSTRAINT check_no_self_follow
            CHECK (follower_id <> following_id)
    );
"""

con = None
cursor = None

try:
    con = db_pool.get_connection()
    cursor = con.cursor()

    cursor.execute(sql)

    print("follows 資料表建立成功或已存在")

except Exception as e:
    print(f"建立 follows 資料表失敗：{e}")
    raise

finally:
    if cursor is not None:
        cursor.close()

    if con is not None:
        con.close()
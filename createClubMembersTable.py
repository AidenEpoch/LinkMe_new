from database import db_pool


sql = """
    CREATE TABLE IF NOT EXISTS club_members (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,
    club_id BIGINT NOT NULL,

    role ENUM('owner', 'admin', 'member')
        NOT NULL DEFAULT 'member',

    joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY uq_club_member (user_id, club_id),

    INDEX idx_club_members_club (club_id),

    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (club_id) REFERENCES clubs(id)
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
    print(f"已經建立 club_members table")
except Exception as e:
    print(f"無法連線至資料庫: {str(e)}")
finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()
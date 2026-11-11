from database import db_pool

sql = """
    CREATE TABLE IF NOT EXISTS follow_requests (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    requester_id BIGINT NOT NULL,
    receiver_id BIGINT NOT NULL,

    status ENUM(
        'pending',
        'accepted',
        'rejected'
    ) NOT NULL DEFAULT 'pending',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    UNIQUE KEY unique_follow_request (
        requester_id,
        receiver_id
    ),

    FOREIGN KEY (requester_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (receiver_id)
        REFERENCES users(id)
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
    print(f"follow_requests table 已經建立")
except Exception as e:
    print(f"無法連線至資料庫: {str(e)}")

finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()
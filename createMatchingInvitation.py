from database import db_pool

con = None
cursor = None
sql = """
    CREATE TABLE matching_invitations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    daily_match_id BIGINT NOT NULL,

    sender_id BIGINT NOT NULL,
    receiver_id BIGINT NOT NULL,

    status ENUM(
        'pending',
        'accepted',
        'rejected'
    ) NOT NULL DEFAULT 'pending',

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    responded_at DATETIME NULL,

    FOREIGN KEY (daily_match_id)
        REFERENCES matching_daily(id),

    FOREIGN KEY (sender_id)
        REFERENCES users(id),

    FOREIGN KEY (receiver_id)
        REFERENCES users(id),

    UNIQUE KEY unique_daily_invitation (
        daily_match_id
    ),

    INDEX idx_receiver_status (
        receiver_id,
        status
    )
);
"""

try:
    con = db_pool.get_connection()
    cursor = con.cursor()
    cursor.execute(sql)
    con.commit()
    print(f"已成功建立matching_invitation table")

except Exception as e:
    print(f"連線失敗: {str(e)}")

finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()
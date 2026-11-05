from database import db_pool

con = None
cursor = None
sql = """
    CREATE TABLE IF NOT EXISTS matching_daily (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    user_id BIGINT NOT NULL,
    matched_user_id BIGINT NOT NULL,

    match_date DATE NOT NULL,

    status ENUM(
        'drawn',
        'invited',
        'skipped'
    ) NOT NULL DEFAULT 'drawn',

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id),

    FOREIGN KEY (matched_user_id)
        REFERENCES users(id),

    UNIQUE KEY unique_daily_match (
        user_id,
        matched_user_id,
        match_date
    ),

    INDEX idx_user_match_date (
        user_id,
        match_date
    )
);
"""

try:
    con = db_pool.get_connection()
    cursor = con.cursor()
    print(f"已成功連線到資料庫")
    cursor.execute(sql)
    con.commit()
    print(f"已成功建立 matching_daily table")


except Exception as e:
    
    print(f"資料庫連線失敗: {str(e)}")
finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()
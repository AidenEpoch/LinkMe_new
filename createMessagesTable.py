from database import db_pool

con = None
cursor = None
sql = """
    CREATE TABLE IF NOT EXISTS messages(
        id BIGINT AUTO_INCREMENT NOT NULL PRIMARY KEY,
        content TEXT NOT NULL,
        sender_id BIGINT NOT NULL,
        conversation_id BIGINT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (sender_id)
            REFERENCES users(id),
        FOREIGN KEY (conversation_id)
            REFERENCES conversations(id),
        INDEX idx_messages_conversation(
            conversation_id, id
        )
    );
"""

try:
    con = db_pool.get_connection()
    cursor = con.cursor()
    print(f"已成功連線上資料庫")
    cursor.execute(sql)
    con.commit()
    print(f"已經建立好 messages table")
    

except Exception as e:
    print(f"無法連線上資料庫:{str(e)}")

finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()
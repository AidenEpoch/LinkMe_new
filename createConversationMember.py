from database import db_pool


con = None
cursor = None
sql = """
    CREATE TABLE IF NOT EXISTS conversation_members(
        conversation_id BIGINT NOT NULL,
        user_id BIGINT NOT NULL,
        PRIMARY KEY (conversation_id, user_id),
        FOREIGN KEY (conversation_id) REFERENCES conversations(id),
        FOREIGN KEY (user_id) REFERENCES users(id)   
    );
"""

try:
    con = db_pool.get_connection()
    cursor = con.cursor()
    print(f"成功連線上資料庫")
    cursor.execute(sql)
    con.commit()
    print(f"已成功建立conversation_members 這個table")

    

except Exception as e:
    print(f"無法連線上資料庫:{str(e)}")

finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()
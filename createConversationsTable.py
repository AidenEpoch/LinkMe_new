from database import db_pool

con = None
cursor = None

sql = """
    CREATE TABLE IF NOT EXISTS conversations(
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
"""

try:
    con = db_pool.get_connection()
    cursor = con.cursor()
    cursor.execute(sql)
    con.commit()

except Exception as e:
    print(f"無法連線到資料庫:{e}")

finally:
    if cursor is not None:
        cursor.close()
    if con is not None:
        con.close()
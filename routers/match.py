from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import json
from database import db_pool
from datetime import datetime
from zoneinfo import ZoneInfo

router = APIRouter()

#############################################  配對 api ##########################################

@router.get("/api/match/remaining")
async def getRemaining(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    today = datetime.now(ZoneInfo("Asia/Taipei")).date()
    sql = """
        SELECT COUNT(*) AS used_count FROM matching_daily WHERE user_id = %s AND match_date = %s;
    """
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        cursor.execute(sql, (user_id, today,))
        result = cursor.fetchone()
        used_count = result["used_count"]
        remaining = max(0, 3 - used_count)
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "remaining": remaining, "used_count": used_count}
        )

    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content = {"error": True, "message": f"伺服器內部錯誤: {str(e)}"}
        )
    finally:
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()


@router.post("/api/match/draw")
async def linkUser(request: Request):
    user_id = request.session.get("user_id")
    if (user_id == None):
        return JSONResponse(
            status_code = 400,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    today = datetime.now(ZoneInfo("Asia/Taipei")).date()
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        con.start_transaction()

        # 鎖定目前會員
        sql = """
            SELECT id
            FROM users
            WHERE id = %s
            FOR UPDATE;
        """

        cursor.execute(sql, (user_id,))

        user = cursor.fetchone()

        if user is None:
            con.rollback()

            return JSONResponse(
                status_code=404,
                content={
                    "error": True,
                    "message": "找不到會員"
                }
            )
        sql = """
            SELECT COUNT(*) AS used_count FROM matching_daily WHERE user_id = %s AND match_date = %s;
        """
        cursor.execute(sql, (user_id, today,))
        result = cursor.fetchone()
        used_count = result["used_count"]
        used_count = int(used_count)
        if(used_count >= 3):
            con.rollback()
            return JSONResponse(
                status_code = 429,
                content = {"error": True, "message": "今天的配對次數已經用完", "remaining": 0}
            )
        remaining = 3 - used_count
        sql = """
            SELECT id, user_name FROM users 
            WHERE id != %s AND id NOT IN (SELECT matched_user_id FROM matching_daily WHERE user_id = %s AND match_date = %s)
            ORDER BY RAND()
            LIMIT 1
        """
        cursor.execute(sql, (user_id, user_id, today,))
        matched_user = cursor.fetchone()

        if matched_user is None:
            con.rollback()
            return JSONResponse(
                status_code = 404,
                content = {"error": True, "message": "目前沒有用戶可供配對"}
            )

        sql = """
            INSERT INTO matching_daily (user_id, matched_user_id, match_date, status) VALUES(%s, %s, %s, %s);
        """
        cursor.execute(sql, (user_id, matched_user["id"], today, "drawn"))
        remaining -= 1
        con.commit()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "成功找到配對對象", "remaining": remaining, "used_count": used_count, "matched_user": matched_user}
        )
        

    except Exception as e:
        if con is not None:
            con.rollback()
        return JSONResponse(
            status_code = 500,
            content = {"error": True, "message": f"伺服器內部錯誤: {str(e)}"}
        )
    finally:
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()
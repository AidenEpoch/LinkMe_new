from database import db_pool
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from zoneinfo import ZoneInfo

router = APIRouter()

@router.get("/api/linkMeGetUser")
async def linkMeGetUser(request: Request, userName: str):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 400,
            content = {"error": True, "message": "尚未登入"}
        )
    print(f"userName:{userName}")
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            SELECT display_name, avatar_url, bio FROM users WHERE user_name = %s;
        """
        cursor.execute(sql,(userName,))
        userData = cursor.fetchone()
        display_name = userData["display_name"]
        avatar_url = userData["avatar_url"]
        bio = userData["bio"]
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "display_name": display_name, "avatar_url": avatar_url, "bio": bio}
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


@router.get("/api/linkme/getAllUser")
async def linkMeGetAllUser(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
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
        sql = """
            SELECT matched_user_id FROM matching_daily WHERE user_id = %s AND match_date = %s;
        """
        cursor.execute(sql, (user_id, today,))
        match_users = cursor.fetchall()
        matched_info = []
        for match_user in match_users:
            sql = """
                SELECT display_name, user_name, avatar_url FROM users WHERE id = %s;
            """
            cursor.execute(sql, (match_user["matched_user_id"],))
            follow_temp = cursor.fetchone()
            user_temp = {}
            user_temp["display_name"] = follow_temp["display_name"]
            user_temp["user_name"] = follow_temp["user_name"]
            user_temp["avatar_url"] = follow_temp["avatar_url"]
            matched_info.append(user_temp)
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "matchedMember": matched_info}
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
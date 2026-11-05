from fastapi import APIRouter, Request
from database import db_pool
from fastapi.responses import JSONResponse


router = APIRouter()

@router.get("/api/getFriendStatus")
async def getFriendStatus(request: Request):
    user_id = request.session["user_id"]
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            SELECT following_id FROM follows WHERE follower_id = %s;
        """
        cursor.execute(sql, (user_id,))
        followings = cursor.fetchall()
        sql = """
            SELECT avatar_url, user_name, display_name FROM users WHERE id = %s ORDER BY updated_time DESC LIMIT 8;
        """
        friends = []
        for following in followings:
            cursor.execute(sql, (following["following_id"],))
            following_one = cursor.fetchone()
            friends.append(following_one)
        print(f"friends: {friends}")
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "friends": friends}
        )
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content = {"error": True, "message": f"伺服器內部錯誤:{str(e)}"}
        )
    finally:
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()

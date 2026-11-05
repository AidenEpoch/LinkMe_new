from database import db_pool
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse



router = APIRouter()


@router.get("/api/notificationGet")
async def notificationGet(request:Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 400,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    sql1 = """
        SELECT COUNT(*) AS notifications FROM notifications WHERE user_id = %s AND is_read = 0;
    """
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        cursor.execute(sql1, (user_id,))
        notifications = cursor.fetchone()
        notifications = notifications["notifications"]
        notifications = int(notifications)
        hasNotification = False
        if(notifications > 0):
            hasNotification = True
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "hasNotification": hasNotification}
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


@router.post("/api/follow/notification/{followingName}")
async def followNotification(request: Request, followingName: str):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 400,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    sql2 = """
        INSERT INTO notifications(user_id, actor_id, type) VALUES(%s, %s, %s);
    """
    sql1 = """
        SELECT id FROM users WHERE user_name = %s;
    """
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        cursor.execute(sql1, (followingName,))
        following_id = cursor.fetchone()
        following_id = following_id["id"]
        cursor.execute(sql2, (following_id, user_id, "follow",))
        con.commit()
        print(f"已將資料寫入notifications table 中")
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已成功追蹤"}
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
    
@router.get("/api/getEditProfileInfo")
async def getEditProfileInfo(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 400,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary= True)
        sql = """
            SELECT display_name, bio, avatar_url FROM users WHERE id = %s;
        """
        cursor.execute(sql, (user_id,))
        print(f"執行sql")
        userInfo = cursor.fetchone()
        print(f"userInfo: {userInfo}")
        display_name = userInfo["display_name"]
        bio = userInfo["bio"]
        avatar_url = userInfo["avatar_url"]
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "display_name": display_name, "bio": bio, "avatar_url": avatar_url}
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
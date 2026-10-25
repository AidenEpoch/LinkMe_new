from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import mysql.connector
import json
from database import db_pool


router = APIRouter()

@router.post("/api/follow/{followingName}")
async def followSomeone(request: Request, followingName: str):
    user_id = request.session["user_id"]
    if (user_id == None):
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
            SELECT id FROM users WHERE user_name = %s;
        """
        cursor.execute(sql, (followingName,))
        followingID = cursor.fetchone()
        followingID = followingID["id"]
        if(followingID == None):
            return JSONResponse(
                status_code = 400,
                content = {"error": True, "message": "查無此用戶", "no_user": True}
            )
        sql = """
            INSERT INTO follows(follower_id, following_id)VALUES(%s, %s);
        """
        cursor.execute(sql, (user_id, followingID,))
        con.commit()
        print(f"已經新增一對追蹤關係")
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已追蹤", "is_follow": True}
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

@router.delete("/api/deleteFollow/{followingName}")
async def deleteFollow(request: Request, followingName: str):
    user_id = request.session["user_id"]
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登陸"}
        )
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            SELECT id FROM users WHERE user_name = %s;
        """
        cursor.execute(sql, (followingName, ))
        followIngID = cursor.fetchone()
        followIngID = followIngID["id"]
        sql = """
            DELETE FROM follows WHERE follower_id = %s AND following_id = %s;
        """
        cursor.execute(sql, (user_id, followIngID, ))
        con.commit()
        sql = """
            SELECT * FROM follows WHERE follower_id = %s AND following_id = %s;
        """
        cursor.execute(sql, (user_id, followIngID, ))
        check = cursor.fetchone()
        if(check is not None):
            print(f"刪除追蹤資料失敗")
            return JSONResponse(
                status_code = 500,
                content = {"fail": True, "message": "刪除資料失敗"}
            )
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已成功刪除追蹤資料"}
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


@router.get("/api/isfollow/{followingName}")
async def checkFollow(request: Request, followingName: str):
    user_id = request.session["user_id"]
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登陸"}
        )
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            SELECT id FROM users WHERE user_name = %s;
        """
        cursor.execute(sql, (followingName, ))
        followingID = cursor.fetchone()
        followingID = followingID["id"]
        sql = """
            SELECT * FROM follows WHERE follower_id = %s AND following_id = %s;
        """
        cursor.execute(sql, (user_id, followingID, ))
        check = cursor.fetchone()
        if(check == None):
            return JSONResponse(
                status = 200,
                content = {"not_follow": True, "messae": "沒有追蹤"}
            )
        else:
            return JSONResponse(
                status_code = 200,
                content = {"is_follow": True, "message": "有追蹤喔"}
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
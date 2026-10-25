from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import mysql.connector
import json
from database import db_pool

router = APIRouter()

cloudfront_name = "d32lm1ug1ggsp6.cloudfront.net"

@router.get("/api/indexPost")
async def getIndexPost(request: Request):
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
        following_id_collect = cursor.fetchall()
        print(f"following_id_collect = {following_id_collect}")
        if(following_id_collect == []):
            print(f"此帳號沒有 follow 其他任何帳號")
            return JSONResponse(
                status_code = 200,
                content = {"no_follow": True, "message": "此帳號沒有 follow 其他任何帳號"}
            )
        sql = """
            SELECT
                p.id,
                p.user_id,
                p.content,
                p.image_key,
                p.created_at,
                u.user_name,
                u.display_name
            FROM posts AS p
            INNER JOIN follows AS f
                ON p.user_id = f.following_id
            INNER JOIN users AS u
                ON p.user_id = u.id
            WHERE f.follower_id = %s
            ORDER BY p.created_at DESC, p.id DESC;
        """
        cursor.execute(sql, (user_id,))
        posts = cursor.fetchall()
        for post in posts:
            post["created_at"] = post["created_at"].isoformat()
            image_key = post["image_key"]

            if not image_key:
                post["image_url"] = None

            elif image_key.startswith(("https://", "http://")):
                post["image_url"] = image_key

            else:
                post["image_url"] = f"https://{cloudfront_name}/{image_key}"
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "posts": posts}
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
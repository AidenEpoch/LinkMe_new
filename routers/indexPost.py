from fastapi import APIRouter, Request, Query
from datetime import datetime
from fastapi.responses import JSONResponse
import mysql.connector
import json
from database import db_pool

router = APIRouter()

cloudfront_name = "d32lm1ug1ggsp6.cloudfront.net"

@router.get("/api/indexPost")
async def getIndexPost(
    request: Request,
    cursor_id: int | None = Query(default = None, ge = 1),
    cursor_time: datetime | None = None
    ):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    if (cursor_id == None) != (cursor_time == None):
        return JSONResponse(
            status_code = 501,
            content = {"error": True, "message": f"游標參數不完整"}
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
        """
        params = []
        params.append(user_id)
        if(cursor_time is not None):
            sql += """
                AND (p.created_at < %s OR (p.created_at = %s AND p.id < %s))
            """
            params.extend([cursor_time, cursor_time, cursor_id])
        sql += """
            ORDER BY p.created_at DESC, p.id DESC
            LIMIT 11;
        """
        cursor.execute(sql, tuple(params))
        posts = cursor.fetchall()

        hasMore = len(posts) > 10
        posts = posts[:10]
        nextCursor = None

        if((hasMore == True) and posts):
            last_post = posts[-1]
            nextCursor = {
                "cursor_time": last_post["created_at"].isoformat(),
                "cursor_id": last_post["id"]
            }

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
            content = {"ok": True, "posts": posts, "hasMore":hasMore, "nextCursor": nextCursor }
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
from fastapi import APIRouter, Request, Form
from database import db_pool
from fastapi.responses import JSONResponse
import json

router = APIRouter()

@router.patch("/api/post/like")
async def postLike(request: Request, post_id: str = Form(...)):
    user_id = request.session.get("user_id")
    if(user_id is None):
        return JSONResponse(
            status_code = 400,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            INSERT INTO post_like(user_id, post_id) VALUES (%s, %s);
        """
        post_id = int(post_id)
        cursor.execute(sql, (user_id, post_id,))
        con.commit()
        sql = """
            SELECT user_id FROM posts WHERE id = %s;
        """
        cursor.execute(sql, (post_id,))
        postOwner_id = cursor.fetchone()["user_id"]
        sql = """
            INSERT INTO notifications (user_id, actor_id, type, post_id) VALUES (%s, %s, %s, %s);
        """
        cursor.execute(sql, (postOwner_id, user_id, "like", post_id,))
        con.commit()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已成功按讚"}
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






@router.patch("/api/post/likeDelete")
async def postLikeDelete(request: Request, post_id: str = Form(...)):
    user_id = request.session.get("user_id")
    if(user_id is None):
        return JSONResponse(
            status_code = 400,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            DELETE FROM post_like WHERE user_id = %s AND post_id = %s;
        """
        post_id = int(post_id)
        cursor.execute(sql, (user_id, post_id,))
        con.commit()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已成功按讚"}
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


from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import JSONResponse
from database import db_pool

router = APIRouter()


def error_response(status, message):
    return JSONResponse(
        status_code=status,
        content={"ok": False, "message": message}
    )



@router.get("/api/post/comments/{post_id}")
def get_post_comments(
    request: Request,
    post_id: int,
    limit: int = Query(default=50, ge=1, le=100)
):
    user_id = request.session.get("user_id")

    if user_id is None:
        return error_response(401, "尚未登入")

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM posts WHERE id = %s",
            (post_id,)
        )

        if cursor.fetchone() is None:
            return error_response(404, "找不到貼文")

        cursor.execute("""
            SELECT
                pc.id,
                pc.post_id,
                pc.user_id,
                pc.content,
                pc.created_at,
                u.user_name,
                u.display_name,
                u.avatar_url
            FROM post_comments AS pc
            JOIN users AS u
                ON pc.user_id = u.id
            WHERE pc.post_id = %s
            ORDER BY pc.created_at DESC, pc.id DESC
            LIMIT %s
        """, (post_id, limit))

        comments = cursor.fetchall()

        for comment in comments:
            comment["created_at"] = (
                comment["created_at"].isoformat()
            )
            comment["is_owner"] = (
                comment["user_id"] == int(user_id)
            )

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM post_comments
            WHERE post_id = %s
        """, (post_id,))

        total = cursor.fetchone()["total"]

        return {
            "ok": True,
            "comments": comments,
            "total": total
        }

    except Exception as e:
        print("取得留言失敗，錯誤原因：", repr(e))
        return error_response(500, "取得留言失敗")

    finally:
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()




@router.post("/api/post/comments")
def create_post_comment(
    request: Request,
    post_id: int = Form(...),
    content: str = Form(...)
):
    user_id = request.session.get("user_id")

    if user_id is None:
        return error_response(401, "尚未登入")

    content = content.strip()

    if not content:
        return error_response(400, "留言不能為空")

    if len(content) > 1000:
        return error_response(400, "留言不能超過1000字")

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        # 取得貼文作者 ID
        cursor.execute("""
            SELECT user_id
            FROM posts
            WHERE id = %s
        """, (post_id,))

        post = cursor.fetchone()

        if post is None:
            return error_response(404, "找不到貼文")

        poster_id = post["user_id"]

        # 新增留言
        cursor.execute("""
            INSERT INTO post_comments
                (post_id, user_id, content)
            VALUES (%s, %s, %s)
        """, (post_id, user_id, content))

        comment_id = cursor.lastrowid

        # 留言者不是貼文作者，才建立通知
        if int(user_id) != int(poster_id):

            cursor.execute("""
                INSERT INTO notifications
                    (
                        user_id,
                        actor_id,
                        type,
                        post_id,
                        comment_id,
                        is_read
                    )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                poster_id,
                user_id,
                "comment",
                post_id,
                comment_id,
                0
            ))

        # 留言與通知一起提交
        con.commit()

        return {
            "ok": True,
            "comment_id": comment_id,
            "message": "留言成功"
        }

    except Exception as e:
        if con is not None:
            con.rollback()

        print("新增留言失敗：", repr(e))
        return error_response(500, "新增留言失敗")

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()




@router.delete("/api/post/comments/{comment_id}")
def delete_post_comment(
    request: Request,
    comment_id: int
):
    user_id = request.session.get("user_id")

    if user_id is None:
        return error_response(401, "尚未登入")

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        cursor.execute("""
            SELECT id
            FROM post_comments
            WHERE id = %s AND user_id = %s
            FOR UPDATE
        """, (comment_id, user_id))

        if cursor.fetchone() is None:
            con.rollback()
            return error_response(404, "找不到留言或沒有刪除權限")

        cursor.execute("""
            DELETE FROM notifications
            WHERE comment_id = %s
            AND type = 'comment'
        """, (comment_id,))
        cursor.execute("""
            DELETE FROM post_comments
            WHERE id = %s AND user_id = %s
        """, (comment_id, user_id))

        deleted = cursor.rowcount

        if deleted == 0:
            con.rollback()
            return error_response(
                404,
                "找不到留言或沒有刪除權限"
            )

        con.commit()

        return {
            "ok": True,
            "message": "留言已刪除"
        }

    except Exception:
        if con is not None:
            con.rollback()
        return error_response(500, "刪除留言失敗")

    finally:
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()

from fastapi import Request, APIRouter, Query
from datetime import datetime
from fastapi.responses import JSONResponse
import json
from database import db_pool

router = APIRouter()

cloudfront_name = "d32lm1ug1ggsp6.cloudfront.net"

PAGE_SIZE = 24

OFFICIAL_ACCOUNTS = (
    "LinkMe",
    "LinkMeSport",
    "LinkMeGame"
)

@router.get("/api/searchPost")
async def getSearchPost(
    request: Request,
    cursor_id: int | None = Query(default=None, ge=1),
    cursor_time: datetime | None = None,
    phase: str = Query(default="following", pattern="^(following|official)$"),
    official_cursor_id: int | None = Query(default=None, ge=1),
    official_cursor_time: datetime | None = None
):
    user_id = request.session.get("user_id")

    if user_id is None:
        return JSONResponse(
            status_code=401,
            content={
                "error": True,
                "message": "尚未登入"
            }
        )

    if (cursor_id is None) != (cursor_time is None):
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": "追蹤貼文游標參數不完整"
            }
        )

    if (official_cursor_id is None) != (official_cursor_time is None):
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": "官方貼文游標參數不完整"
            }
        )

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        posts = []
        following_has_more = False


        if phase == "following":

            sql = """
                SELECT
                    p.id,
                    p.user_id,
                    p.content,
                    p.image_key,
                    p.created_at,
                    u.user_name,
                    u.display_name,
                    u.avatar_url,

                EXISTS (
                    SELECT 1
                    FROM post_like AS pl
                    WHERE pl.post_id = p.id
                    AND pl.user_id = %s
                ) AS is_liked
                FROM posts AS p
                INNER JOIN users AS u
                    ON p.user_id = u.id
                WHERE EXISTS (
                    SELECT 1
                    FROM follows AS f
                    WHERE f.follower_id = %s
                      AND f.following_id = p.user_id
                )
            """

            params = [user_id, user_id]

            if cursor_time is not None:
                sql += """
                    AND (
                        p.created_at < %s
                        OR (
                            p.created_at = %s
                            AND p.id < %s
                        )
                    )
                """

                params.extend([
                    cursor_time,
                    cursor_time,
                    cursor_id
                ])

            sql += """
                ORDER BY p.created_at DESC, p.id DESC
                LIMIT %s
            """

            params.append(PAGE_SIZE + 1)   

            cursor.execute(sql, tuple(params))

            following_posts = cursor.fetchall()

            following_has_more = len(following_posts) > PAGE_SIZE   

            posts = following_posts[:PAGE_SIZE]


        remaining = PAGE_SIZE - len(posts)

        official_has_more = False

        if remaining > 0 and not following_has_more:

            sql = """
                SELECT
                    p.id,
                    p.user_id,
                    p.content,
                    p.image_key,
                    p.created_at,
                    u.user_name,
                    u.display_name,
                    u.avatar_url,
                 EXISTS (
                    SELECT 1
                    FROM post_like AS pl
                    WHERE pl.post_id = p.id
                    AND pl.user_id = %s
                ) AS is_liked
                FROM posts AS p
                INNER JOIN users AS u
                    ON p.user_id = u.id
                WHERE u.user_name IN (%s, %s, %s)

                  AND NOT EXISTS (
                      SELECT 1
                      FROM follows AS f
                      WHERE f.follower_id = %s
                        AND f.following_id = p.user_id
                  )
            """

            params = [
                user_id,
                *OFFICIAL_ACCOUNTS,
                user_id
            ]

            if official_cursor_time is not None:

                sql += """
                    AND (
                        p.created_at < %s
                        OR (
                            p.created_at = %s
                            AND p.id < %s
                        )
                    )
                """

                params.extend([
                    official_cursor_time,
                    official_cursor_time,
                    official_cursor_id
                ])

            sql += """
                ORDER BY p.created_at DESC, p.id DESC
                LIMIT %s
            """

            params.append(remaining + 1)

            cursor.execute(sql, tuple(params))

            official_posts = cursor.fetchall()

            official_has_more = len(official_posts) > remaining

            posts.extend(official_posts[:remaining])


        nextCursor = None
        hasMore = False

        if following_has_more:
            last_post = posts[-1]

            hasMore = True

            nextCursor = {
                "phase": "following",
                "cursor_time": last_post["created_at"].isoformat(),
                "cursor_id": last_post["id"]
            }

        elif official_has_more:
            last_official_post = posts[-1]

            hasMore = True

            nextCursor = {
                "phase": "official",
                "official_cursor_time": last_official_post["created_at"].isoformat(),
                "official_cursor_id": last_official_post["id"]
            }

        for post in posts:
            post["is_liked"] = bool(post["is_liked"])
            
            post["created_at"] = post["created_at"].isoformat()

            image_key = post["image_key"]

            if not image_key:
                post["image_url"] = None

            elif image_key.startswith(("https://", "http://")):
                post["image_url"] = image_key

            else:
                post["image_url"] = (
                    f"https://{cloudfront_name}/{image_key.lstrip('/')}"
                )

        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "posts": posts,
                "hasMore": hasMore,
                "nextCursor": nextCursor
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": f"伺服器內部錯誤: {str(e)}"
            }
        )

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()
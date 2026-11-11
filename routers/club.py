
from fastapi import APIRouter, Request, Form, Query
from fastapi.responses import JSONResponse
from database import db_pool

router = APIRouter(prefix="/api/clubs", tags=["clubs"])


def error_response(status, message):
    return JSONResponse(
        status_code=status,
        content={"ok": False, "message": message}
    )


def get_user_id(request):
    return request.session.get("user_id")


@router.post("")
def create_club(
    request: Request,
    name: str = Form(...),
    club_type: str = Form(""),
    description: str = Form(""),
    img_url: str = Form("")
):
    user_id = get_user_id(request)

    if user_id is None:
        return error_response(401, "請先登入")

    name = name.strip()
    club_type = club_type.strip()
    description = description.strip()
    img_url = img_url.strip()

    if not 1 <= len(name) <= 256:
        return error_response(400, "社群名稱需為 1～256 字")

    if len(club_type) > 100:
        return error_response(400, "分類最多 100 字")

    if len(description) > 2000:
        return error_response(400, "簡介最多 2000 字")

    if len(img_url) > 1024:
        return error_response(400, "圖片網址過長")

    if img_url and not img_url.startswith(("https://", "http://")):
        return error_response(400, "請使用有效的圖片網址")

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor()

        cursor.execute("""
            INSERT INTO clubs
                (name, type, description, img_url, owner_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            name,
            club_type or None,
            description or None,
            img_url or None,
            user_id
        ))

        club_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO club_members
                (user_id, club_id, role)
            VALUES (%s, %s, 'owner')
        """, (user_id, club_id))

        con.commit()

        return {
            "ok": True,
            "club_id": club_id,
            "message": "建立社群成功"
        }

    except Exception as error:
        if con:
            con.rollback()
        print("建立社群錯誤:", repr(error))
        return error_response(500, "建立社群失敗")

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


@router.get("")
def get_clubs(
    request: Request,
    cursor: int | None = Query(None, ge=1),
    limit: int = Query(12, ge=1, le=30),
    keyword: str = Query("", max_length=100)
):
    user_id = get_user_id(request)

    if user_id is None:
        return error_response(401, "請先登入")

    con = None
    db_cursor = None

    try:
        con = db_pool.get_connection()
        db_cursor = con.cursor(dictionary=True)

        conditions = []
        params = []

        if cursor is not None:
            conditions.append("c.id < %s")
            params.append(cursor)

        if keyword.strip():
            # 跳脫 LIKE 特殊字元
            escaped = (
                keyword.strip()
                .replace("\\", "\\\\")
                .replace("%", "\\%")
                .replace("_", "\\_")
            )
            conditions.append("c.name LIKE %s")
            params.append(f"%{escaped}%")

        where_sql = (
            "WHERE " + " AND ".join(conditions)
            if conditions else ""
        )

        sql = f"""
            SELECT
                c.id,
                c.name,
                c.type,
                c.description,
                c.img_url,
                c.owner_id,
                c.created_at,

                (
                    SELECT COUNT(*)
                    FROM club_members cm
                    WHERE cm.club_id = c.id
                ) AS member_count,

                (
                    SELECT cm2.role
                    FROM club_members cm2
                    WHERE cm2.club_id = c.id
                      AND cm2.user_id = %s
                    ORDER BY cm2.id
                    LIMIT 1
                ) AS my_role

            FROM clubs c
            {where_sql}
            ORDER BY c.id DESC
            LIMIT %s
        """

        db_cursor.execute(
            sql,
            (user_id, *params, limit + 1)
        )

        rows = db_cursor.fetchall()

        has_more = len(rows) > limit
        rows = rows[:limit]

        for row in rows:
            row["is_member"] = row["my_role"] is not None
            row["created_at"] = row["created_at"].isoformat()

        next_cursor = (
            rows[-1]["id"]
            if has_more and rows
            else None
        )

        return {
            "ok": True,
            "clubs": rows,
            "hasMore": has_more,
            "nextCursor": next_cursor
        }

    except Exception as error:
        print("取得社群錯誤:", repr(error))
        return error_response(500, "取得社群失敗")

    finally:
        if db_cursor:
            db_cursor.close()
        if con:
            con.close()


@router.get("/mine")
def get_my_clubs(request: Request):
    user_id = get_user_id(request)

    if user_id is None:
        return error_response(401, "請先登入")

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                c.id,
                c.name,
                c.type,
                c.img_url,
                c.owner_id,
                cm.role
            FROM club_members cm
            JOIN clubs c ON c.id = cm.club_id
            WHERE cm.user_id = %s
            ORDER BY cm.joined_at DESC, cm.id DESC
        """, (user_id,))

        return {
            "ok": True,
            "clubs": cursor.fetchall()
        }

    except Exception as error:
        print("我的社群錯誤:", repr(error))
        return error_response(500, "取得我的社群失敗")

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


@router.post("/{club_id}/join")
def join_club(club_id: int, request: Request):
    user_id = get_user_id(request)

    if user_id is None:
        return error_response(401, "請先登入")

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        # 以社群列作為加入操作的鎖定點
        cursor.execute("""
            SELECT id
            FROM clubs
            WHERE id = %s
            FOR UPDATE
        """, (club_id,))

        if cursor.fetchone() is None:
            con.rollback()
            return error_response(404, "社群不存在")

        cursor.execute("""
            SELECT id
            FROM club_members
            WHERE club_id = %s AND user_id = %s
            LIMIT 1
        """, (club_id, user_id))

        if cursor.fetchone() is not None:
            con.commit()
            return {
                "ok": True,
                "message": "你已經是社群成員"
            }

        cursor.execute("""
            INSERT INTO club_members
                (user_id, club_id, role)
            VALUES (%s, %s, 'member')
        """, (user_id, club_id))

        con.commit()

        return {
            "ok": True,
            "message": "加入社群成功"
        }

    except Exception as error:
        if con:
            con.rollback()
        print("加入社群錯誤:", repr(error))
        return error_response(500, "加入社群失敗")

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


@router.delete("/{club_id}/leave")
def leave_club(club_id: int, request: Request):
    user_id = get_user_id(request)

    if user_id is None:
        return error_response(401, "請先登入")

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        cursor.execute("""
            SELECT owner_id
            FROM clubs
            WHERE id = %s
            FOR UPDATE
        """, (club_id,))

        club = cursor.fetchone()

        if club is None:
            con.rollback()
            return error_response(404, "社群不存在")

        if int(club["owner_id"]) == int(user_id):
            con.rollback()
            return error_response(
                400,
                "社群建立者不能退出自己的社群"
            )

        cursor.execute("""
            DELETE FROM club_members
            WHERE club_id = %s AND user_id = %s
        """, (club_id, user_id))

        con.commit()

        return {
            "ok": True,
            "message": "已退出社群"
        }

    except Exception as error:
        if con:
            con.rollback()
        print("退出社群錯誤:", repr(error))
        return error_response(500, "退出社群失敗")

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

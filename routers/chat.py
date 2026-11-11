import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from database import db_pool
from fastapi import WebSocket, WebSocketDisconnect

router = APIRouter()


@router.get("/api/chat/conversations")
async def get_conversations(request: Request):

    user_id = request.session.get("user_id")

    if user_id is None:
        return JSONResponse(
            status_code=401,
            content={"error": True, "message": "尚未登入"}
        )

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        sql = """
            SELECT
                c.id AS conversation_id,
                u.id AS other_user_id,
                u.user_name,
                u.display_name,
                u.avatar_url,

                (
                    SELECT m.content
                    FROM messages AS m
                    WHERE m.conversation_id = c.id
                    ORDER BY m.id DESC
                    LIMIT 1
                ) AS last_message,

            (
                SELECT m.created_at
                FROM messages AS m
                WHERE m.conversation_id = c.id
                ORDER BY m.id DESC
                LIMIT 1
            ) AS last_message_at,

            (
                SELECT COUNT(*)
                FROM messages AS unread
                WHERE unread.conversation_id = c.id
                AND unread.sender_id != mine.user_id
                AND unread.id > COALESCE(
                    mine.last_read_message_id, 0
                )
            ) AS unread_count


            FROM conversations AS c

            INNER JOIN conversation_members AS mine
                ON mine.conversation_id = c.id
                AND mine.user_id = %s

            INNER JOIN conversation_members AS other
                ON other.conversation_id = c.id
                AND other.user_id != %s

            INNER JOIN users AS u
                ON u.id = other.user_id

            WHERE (
                SELECT COUNT(*)
                FROM conversation_members AS cm
                WHERE cm.conversation_id = c.id
            ) = 2

            ORDER BY
                COALESCE(last_message_at, c.created_at) DESC,
                c.id DESC;
        """

        cursor.execute(sql, (user_id, user_id))
        conversations = cursor.fetchall()

        for conversation in conversations:
            if conversation["last_message_at"] is not None:
                conversation["last_message_at"] = (
                    conversation["last_message_at"].isoformat()
                )

        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "conversations": conversations
            }
        )

    except Exception as e:
        print("取得聊天列表失敗:", repr(e))

        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "伺服器內部錯誤"
            }
        )

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()




from fastapi import Form

@router.post("/api/chat/conversations")
async def create_conversation(
    request: Request,
    other_user_id: int = Form(...)
):
    user_id = request.session.get("user_id")

    if user_id is None:
        return JSONResponse(
            status_code=401,
            content={"error": True, "message": "尚未登入"}
        )

    if user_id == other_user_id:
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": "不能與自己建立對話"}
        )

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        # 確認對方存在
        cursor.execute(
            "SELECT id FROM users WHERE id = %s",
            (other_user_id,)
        )

        if cursor.fetchone() is None:
            return JSONResponse(
                status_code=404,
                content={"error": True, "message": "找不到此使用者"}
            )

        # 查詢兩人是否已有一對一對話
        sql = """
            SELECT cm1.conversation_id
            FROM conversation_members AS cm1
            INNER JOIN conversation_members AS cm2
                ON cm1.conversation_id = cm2.conversation_id
            WHERE cm1.user_id = %s
              AND cm2.user_id = %s
              AND (
                  SELECT COUNT(*)
                  FROM conversation_members AS cm3
                  WHERE cm3.conversation_id = cm1.conversation_id
              ) = 2
            LIMIT 1;
        """

        cursor.execute(sql, (user_id, other_user_id))
        existing = cursor.fetchone()

        if existing is not None:
            return JSONResponse(
                status_code=200,
                content={
                    "ok": True,
                    "conversation_id": existing["conversation_id"],
                    "created": False
                }
            )

        # 建立新對話
        cursor.execute(
            "INSERT INTO conversations () VALUES ()"
        )

        conversation_id = cursor.lastrowid

        # 加入兩位參與者
        sql = """
            INSERT INTO conversation_members
            (conversation_id, user_id)
            VALUES (%s, %s);
        """

        cursor.execute(sql, (conversation_id, user_id))
        cursor.execute(sql, (conversation_id, other_user_id))

        con.commit()

        return JSONResponse(
            status_code=201,
            content={
                "ok": True,
                "conversation_id": conversation_id,
                "created": True
            }
        )

    except Exception as e:
        if con is not None:
            con.rollback()

        print("建立聊天對話失敗:", repr(e))

        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "建立聊天對話失敗"}
        )

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()


@router.get("/api/chat/conversations/{conversation_id}/messages")
async def get_chat_messages(
    request: Request,
    conversation_id: int
):
    user_id = request.session.get("user_id")

    if user_id is None:
        return JSONResponse(
            status_code=401,
            content={"error": True, "message": "尚未登入"}
        )

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        # 確認目前使用者有參與這個對話
        sql = """
            SELECT 1
            FROM conversation_members
            WHERE conversation_id = %s
              AND user_id = %s;
        """
        cursor.execute(sql, (conversation_id, user_id))

        if cursor.fetchone() is None:
            return JSONResponse(
                status_code=403,
                content={
                    "error": True,
                    "message": "沒有權限查看此對話"
                }
            )

        # 取得歷史訊息
        sql = """
            SELECT
                id,
                conversation_id,
                sender_id,
                content,
                created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY id ASC;
        """

        cursor.execute(sql, (conversation_id,))
        messages = cursor.fetchall()

        for message in messages:
            if message["created_at"] is not None:
                message["created_at"] = (
                    message["created_at"].isoformat()
                )

        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "conversation_id": conversation_id,
                "messages": messages
            }
        )

    except Exception as e:
        print("取得歷史訊息失敗:", repr(e))

        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "取得歷史訊息失敗"
            }
        )

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()





# 儲存目前連線中的使用者
# 同一個使用者可能開啟多個分頁
active_connections = {}
connections_lock = asyncio.Lock()


@router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):

    user_id = websocket.session.get("user_id")

    if user_id is None:
        await websocket.close(code=1008)
        return

    user_id = int(user_id)

    await websocket.accept()

    async with connections_lock:
        active_connections.setdefault(user_id, set()).add(websocket)

    print(f"使用者 {user_id} 已連線")

    try:
        while True:
            raw_message = await websocket.receive_text()

            try:
                data = json.loads(raw_message)
                conversation_id = int(data["conversation_id"])
                content = data["content"]

                if (
                    not isinstance(content, str)
                    or not content.strip()
                    or len(content) > 5000
                ):
                    raise ValueError("訊息內容不合法")

            except (ValueError, KeyError, TypeError, json.JSONDecodeError):
                await websocket.send_json({
                    "ok": False,
                    "message": "訊息格式不正確"
                })
                continue

            con = None
            cursor = None

            try:
                con = db_pool.get_connection()
                cursor = con.cursor(dictionary=True)

                # 確認目前使用者屬於此對話
                cursor.execute("""
                    SELECT 1
                    FROM conversation_members
                    WHERE conversation_id = %s
                      AND user_id = %s
                """, (conversation_id, user_id))

                if cursor.fetchone() is None:
                    await websocket.send_json({
                        "ok": False,
                        "message": "沒有權限傳送訊息"
                    })
                    continue

                # 取得對話的所有參與者
                cursor.execute("""
                    SELECT user_id
                    FROM conversation_members
                    WHERE conversation_id = %s
                """, (conversation_id,))

                members = [
                    row["user_id"]
                    for row in cursor.fetchall()
                ]

                if len(members) != 2:
                    await websocket.send_json({
                        "ok": False,
                        "message": "目前只支援一對一聊天"
                    })
                    continue

                # 儲存訊息
                cursor.execute("""
                    INSERT INTO messages
                    (conversation_id, sender_id, content)
                    VALUES (%s, %s, %s)
                """, (conversation_id, user_id, content.strip()))

                message_id = cursor.lastrowid

                cursor.execute("""
                    SELECT created_at
                    FROM messages
                    WHERE id = %s
                """, (message_id,))

                created_at = cursor.fetchone()["created_at"]

                con.commit()

            except Exception as e:
                if con is not None:
                    con.rollback()

                print("傳送聊天訊息失敗:", repr(e))

                await websocket.send_json({
                    "ok": False,
                    "message": "訊息儲存失敗"
                })
                continue

            finally:
                if cursor is not None:
                    cursor.close()

                if con is not None:
                    con.close()

            # 訊息儲存成功後，通知雙方
            payload = {
                "ok": True,
                "type": "new_message",
                "message": {
                    "id": message_id,
                    "conversation_id": conversation_id,
                    "sender_id": user_id,
                    "content": content.strip(),
                    "created_at": created_at.isoformat()
                }
            }

            async with connections_lock:
                recipients = [
                    connection
                    for member_id in members
                    for connection in active_connections.get(member_id, set())
                ]

            for connection in recipients:
                try:
                    await connection.send_json(payload)
                except Exception:
                    print("部分使用者的 WebSocket 已中斷")

    except WebSocketDisconnect:
        print(f"使用者 {user_id} 已離線")

    finally:
        async with connections_lock:
            user_connections = active_connections.get(user_id)

            if user_connections is not None:
                user_connections.discard(websocket)

                if not user_connections:
                    del active_connections[user_id]



@router.post("/api/chat/conversations/{conversation_id}/read")
async def mark_conversation_read(
    request: Request,
    conversation_id: int
):
    user_id = request.session.get("user_id")

    if user_id is None:
        return JSONResponse(
            status_code=401,
            content={"ok": False, "message": "尚未登入"}
        )

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        # 確認使用者屬於這個對話
        cursor.execute("""
            SELECT last_read_message_id
            FROM conversation_members
            WHERE conversation_id = %s
              AND user_id = %s
        """, (conversation_id, user_id))

        member = cursor.fetchone()

        if member is None:
            return JSONResponse(
                status_code=403,
                content={"ok": False, "message": "沒有權限查看此對話"}
            )

        # 取得這個對話最新一則訊息的 ID
        cursor.execute("""
            SELECT MAX(id) AS latest_message_id
            FROM messages
            WHERE conversation_id = %s
        """, (conversation_id,))

        latest_message_id = cursor.fetchone()["latest_message_id"]

        # 避免把已讀進度倒退，也處理沒有訊息的對話
        last_read_message_id = max(
            member["last_read_message_id"] or 0,
            latest_message_id or 0
        )

        # 更新目前使用者的已讀進度
        cursor.execute("""
            UPDATE conversation_members
            SET last_read_message_id = %s
            WHERE conversation_id = %s
              AND user_id = %s
        """, (
            last_read_message_id or None,
            conversation_id,
            user_id
        ))

        con.commit()

        return {
            "ok": True,
            "conversation_id": conversation_id,
            "last_read_message_id": last_read_message_id or None
        }

    except Exception as e:
        if con is not None:
            con.rollback()

        print("標記訊息已讀失敗:", repr(e))

        return JSONResponse(
            status_code=500,
            content={"ok": False, "message": "標記已讀失敗"}
        )

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()



@router.get("/api/chat/me")
async def get_chat_me(request: Request):

    user_id = request.session.get("user_id")

    if user_id is None:
        return {
            "ok": False,
            "message": "尚未登入"
        }

    return {
        "ok": True,
        "user_id": int(user_id)
    }

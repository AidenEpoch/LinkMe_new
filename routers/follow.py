from fastapi import APIRouter, Request, Form
from fastapi.responses import JSONResponse
import mysql.connector
import json
from database import db_pool


router = APIRouter()


@router.post("/api/follow/{followingName}")
async def followSomeone(request: Request, followingName: str):
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

        # 取得被追蹤者的資料
        sql = """
            SELECT id, is_private
            FROM users
            WHERE user_name = %s;
        """
        cursor.execute(sql, (followingName,))
        following_data = cursor.fetchone()

        if following_data is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": True,
                    "no_user": True,
                    "message": "查無此用戶"
                }
            )

        followingID = following_data["id"]
        is_private = following_data["is_private"]

        if followingID == user_id:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "不能追蹤自己"}
            )

        # 先檢查是否已經追蹤
        sql = """
            SELECT 1
            FROM follows
            WHERE follower_id = %s
            AND following_id = %s;
        """
        cursor.execute(sql, (user_id, followingID))
        existing_follow = cursor.fetchone()

        if existing_follow is not None:
            return JSONResponse(
                status_code=200,
                content={
                    "ok": True,
                    "is_follow": True,
                    "message": "已經追蹤此用戶"
                }
            )

        # 私人帳戶
        if is_private:
            sql = """
                SELECT status
                FROM follow_requests
                WHERE requester_id = %s
                AND receiver_id = %s;
            """
            cursor.execute(sql, (user_id, followingID))
            existing_request = cursor.fetchone()

            if existing_request is not None:
                status = existing_request["status"]

                if status == "pending":
                    return JSONResponse(
                        status_code=200,
                        content={
                            "ok": True,
                            "wait_for_follow": True,
                            "message": "已送出追蹤申請"
                        }
                    )


                if status in ("rejected", "accepted"):
                    sql = """
                        UPDATE follow_requests
                        SET status = %s
                        WHERE requester_id = %s
                        AND receiver_id = %s;
                    """
                    cursor.execute(
                        sql,
                        ("pending", user_id, followingID)
                    )
                else:
                    return JSONResponse(
                        status_code=409,
                        content={
                            "error": True,
                            "message": "無法處理目前的申請狀態"
                        }
                    )

            else:
                sql = """
                    INSERT INTO follow_requests
                    (requester_id, receiver_id, status)
                    VALUES (%s, %s, %s);
                """
                cursor.execute(
                    sql, (user_id, followingID, "pending")
                )

            # 建立追蹤申請通知
            sql = """
                INSERT INTO notifications
                (user_id, actor_id, type)
                VALUES (%s, %s, %s);
            """
            cursor.execute(
                sql, (followingID, user_id, "follow_checking")
            )

            con.commit()

            return JSONResponse(
                status_code=200,
                content={
                    "ok": True,
                    "wait_for_follow": True,
                    "message": "已送出追蹤申請"
                }
            )

        # 公開帳戶
        else:
            sql = """
                INSERT INTO follows
                (follower_id, following_id)
                VALUES (%s, %s);
            """
            cursor.execute(sql, (user_id, followingID))
            con.commit()

            return JSONResponse(
                status_code=200,
                content={
                    "ok": True,
                    "is_follow": True,
                    "message": "已追蹤"
                }
            )

    except mysql.connector.IntegrityError as e:
        if con is not None:
            con.rollback()

        print("追蹤資料庫錯誤:", repr(e))

        if e.errno == 1062:
            return JSONResponse(
                status_code=409,
                content={
                    "error": True,
                    "message": "資料已存在，請重新整理頁面"
                }
            )

        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "資料庫操作失敗"}
        )

    except Exception as e:
        if con is not None:
            con.rollback()

        print("追蹤發生錯誤:", repr(e))

        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()


@router.delete("/api/deleteFollow/{followingName}")
async def deleteFollow(request: Request, followingName: str):
    user_id = request.session.get("user_id")
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
    user_id = request.session.get("user_id")
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
        cursor.execute(sql, (user_id, followingID,))
        check = cursor.fetchone()

        sql = """
            SELECT * FROM follow_requests WHERE requester_id = %s AND receiver_id = %s;
        """
        cursor.execute(sql, (user_id, followingID,))
        isWaiting = cursor.fetchone()
        
        if(check is not None):
            return JSONResponse(
                status_code = 200,
                content = {"is_follow": True, "message": "有追蹤喔"}
            )
        
        if isWaiting is not None:
            if isWaiting["status"] == "pending":
                return JSONResponse(
                    status_code=200,
                    content={
                        "not_follow": True,
                        "is_waiting": True,
                        "message": "等待對方審核"
                    }
                )
        return JSONResponse(
                status_code=200,
                content={
                    "not_follow": True,
                    "is_waiting": False,
                    "message": "尚未追蹤"
                }
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

@router.patch("/api/private/follow")
async def privateFollowAccept(request: Request, actor_id: int = Form(...), receiver_id: int = Form(), notification_id: int = Form()):
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
            UPDATE follow_requests SET status = %s WHERE requester_id = %s AND receiver_id = %s;
        """
        cursor.execute(sql, ("accepted", actor_id, receiver_id,))
        sql = """
            UPDATE notifications SET is_read = 1 WHERE id = %s;
        """
        cursor.execute(sql, (notification_id,))
        sql = """
            INSERT INTO follows (follower_id, following_id) VALUES (%s, %s);
        """
        cursor.execute(sql, (actor_id, receiver_id,))
        con.commit()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已經成功追蹤私人帳號"}
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


@router.patch("/api/private/cancel/{user_name}")
async def privateFollowCancel(request: Request, user_name: str):
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
            SELECT id FROM users WHERE user_name = %s;
        """
        cursor.execute(sql, (user_name,))
        user_data = cursor.fetchone()
        if(user_data is None):
            return JSONResponse(
                status_code = 400,
                content = {"error": True, "message": "找不到此用戶"}
            )
        actor_id = user_data["id"]
        sql = """
            DELETE FROM notifications WHERE type = %s AND user_id = %s AND actor_id = %s;
        """
        cursor.execute(sql, ("follow_checking", actor_id, user_id,))
        sql = """
            DELETE FROM follow_requests WHERE requester_id = %s AND receiver_id = %s;
        """
        cursor.execute(sql, (user_id, actor_id,))
        con.commit()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已取消追蹤私人帳戶"}
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




@router.patch("/api/private/reject")
async def privateFollowReject(
    request: Request,
    actor_id: int = Form(...)
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

        # 只允許私人帳戶本人拒絕收到的申請
        sql = """
            UPDATE follow_requests
            SET status = %s
            WHERE requester_id = %s
            AND receiver_id = %s
            AND status = %s;
        """
        cursor.execute(
            sql,
            ("rejected", actor_id, user_id, "pending")
        )

        if cursor.rowcount == 0:
            con.rollback()
            return JSONResponse(
                status_code=404,
                content={
                    "error": True,
                    "message": "找不到待審核的追蹤申請"
                }
            )

        # 將對應的追蹤申請通知標記為已讀
        sql = """
            UPDATE notifications
            SET is_read = 1
            WHERE user_id = %s
            AND actor_id = %s
            AND type = %s;
        """
        cursor.execute(
            sql,
            (user_id, actor_id, "follow_checking")
        )

        con.commit()

        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "message": "已拒絕追蹤申請"
            }
        )

    except Exception as e:
        if con is not None:
            con.rollback()

        print("拒絕追蹤申請失敗:", repr(e))

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
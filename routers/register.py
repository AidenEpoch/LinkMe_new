from email_sender import send_verification_email
from email_validator import is_valid_email
from email_verification_service import (
    generate_verification_code,
    hash_verification_code,
    get_expiration_time,
    RESEND_COOLDOWN_SECONDS
)
from email_verification_service import verify_code_hash, MAX_VERIFY_ATTEMPTS
from datetime import datetime, timezone


from fastapi import APIRouter, Request, Form, Body
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import json
from database import db_pool
from argon2 import PasswordHasher
from argon2.exceptions import (VerifyMismatchError, VerificationError)
from starlette.middleware.sessions import SessionMiddleware

ph = PasswordHasher()

router = APIRouter()

################################# 註冊的api ###########################################

### requirements: {"userName": userName, "password": password, "email": email}

@router.post("/api/register")
async def register(
    request: Request,
    requirements: dict = Body(
        ...,
        examples=[{
            "userName": "test123",
            "password": "Test123456!",
            "email": "abc@gmail"
        }]
    )
):
    requirements = await request.json()

    user_name = requirements.get("userName")
    email = requirements.get("email")
    password = requirements.get("password")

    if not all(isinstance(v, str) and v.strip()
               for v in (user_name, email, password)):
        return JSONResponse(
            status_code=400,
            content={"ok": False, "message": "註冊資料不可留白"}
        )

    user_name = user_name.strip()
    email = email.strip().lower()

    # 檢查 Email 格式是否正確
    if not is_valid_email(email):
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "message": "請輸入正確的 Email 格式"
            }
        )

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        # 檢查帳號是否已存在
        cursor.execute(
            """
            SELECT id FROM users
            WHERE email = %s OR user_name = %s
            LIMIT 1
            """,
            (email, user_name)
        )

        if cursor.fetchone():
            return JSONResponse(
                status_code=409,
                content={"ok": False, "message": "Email 或用戶名稱已被使用"}
            )

        password_hash = ph.hash(password)

        # 建立會員，預設尚未驗證
        cursor.execute(
            """
            INSERT INTO users
            (user_name, email, password_hash,
             display_name, avatar_url, is_verified)
            VALUES (%s, %s, %s, %s, %s, 0)
            """,
            (
                user_name,
                email,
                password_hash,
                user_name,
                "/static/image/avatar_default.png"
            )
        )

        user_id = cursor.lastrowid

        # 產生六位數驗證碼
        code = generate_verification_code()
        code_hash = hash_verification_code(user_id, code)
        expires_at = get_expiration_time()

        # 將驗證碼雜湊值存入資料庫
        cursor.execute(
            """
            INSERT INTO email_verifications
            (user_id, code_hash, expires_at)
            VALUES (%s, %s, %s)
            """,
            (user_id, code_hash, expires_at)
        )

        # 先讓 SES 接受寄信請求，再提交資料庫交易
        send_verification_email(email, code)

        con.commit()

        return JSONResponse(
            status_code=201,
            content={
                "ok": True,
                "message": "註冊成功，請完成 Email 驗證",
                "verificationRequired": True
            }
        )

    except Exception as e:
        print(f"註冊 API 發生錯誤：{type(e).__name__}: {e}")

        if con is not None:
            con.rollback()

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "message": "伺服器內部錯誤"
            }
        )

    finally:
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()


############################### 註冊的api 結束 #######################################



#############################  修改密碼  ###########################################

@router.post("/api/edit/account/password_check")
async def checkOldPassword(request: Request, oldPassword: str = Form()):
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
            SELECT password_hash FROM users WHERE id = %s;
        """
        cursor.execute(sql, (user_id,))
        password_hash = cursor.fetchone()
        password_hash = password_hash["password_hash"]
        try:
            ph.verify(password_hash, oldPassword)
            print("驗證成功")
        except(VerifyMismatchError, ValueError):
            return JSONResponse(
                status_code = 401,
                content = {"error": True, "message": "帳號或密碼錯誤"}
            )
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "密碼確認成功"}
        )
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content = {"error": True, "message": f"{str(e)}"}
        )
    finally:
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()


@router.patch("/api/edit/account/password")
async def editPassword(request: Request, newPassword: str = Form()):
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
        password_hash = newPassword
        password_hash = ph.hash(password_hash)
        print(f"修改後的密碼的hash: {password_hash}")
        sql = """
            UPDATE users SET password_hash = %s WHERE id = %s;
        """
        cursor.execute(sql, (password_hash, user_id,))
        con.commit()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "密碼修改成功"}
        )
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content = {"error": True, "message": f"{str(e)}"}
        )
    finally:
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()




@router.post("/api/verify-email")
async def verify_email(
    data: dict = Body(
        ...,
        examples=[
            {
                "email": "test@example.com",
                "code": "123456"
            }
        ]
    )
):
    email = data.get("email")
    code = data.get("code")

    if not isinstance(email, str) or not isinstance(code, str):
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "message": "資料格式錯誤"
            }
        )

    email = email.strip().lower()

    if (
        not email
        or len(code) != 6
        or not code.isascii()
        or not code.isdigit()
    ):
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "message": "請輸入六位數驗證碼"
            }
        )

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        # 鎖定會員資料，避免同時驗證
        cursor.execute(
            """
            SELECT id, is_verified
            FROM users
            WHERE email = %s
            LIMIT 1
            FOR UPDATE
            """,
            (email,)
        )

        user = cursor.fetchone()

        if user is None:
            con.rollback()
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "message": "驗證資料無效"
                }
            )

        if user["is_verified"]:
            con.rollback()
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "message": "此帳號已完成驗證"
                }
            )

        cursor.execute(
            """
            SELECT code_hash, expires_at, attempts
            FROM email_verifications
            WHERE user_id = %s
            FOR UPDATE
            """,
            (user["id"],)
        )

        verification = cursor.fetchone()

        if verification is None:
            con.rollback()
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "message": "找不到驗證碼"
                }
            )

        if verification["attempts"] >= MAX_VERIFY_ATTEMPTS:
            con.rollback()
            return JSONResponse(
                status_code=429,
                content={
                    "ok": False,
                    "message": "驗證次數過多，請重新取得驗證碼"
                }
            )

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if now >= verification["expires_at"]:
            con.rollback()
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "message": "驗證碼已過期，請重新取得驗證碼"
                }
            )

        # 驗證使用者輸入的六位數字
        if not verify_code_hash(
            user["id"],
            code,
            verification["code_hash"]
        ):
            cursor.execute(
                """
                UPDATE email_verifications
                SET attempts = attempts + 1
                WHERE user_id = %s
                """,
                (user["id"],)
            )

            con.commit()

            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "message": "驗證碼錯誤"
                }
            )

        # 驗證成功，更新會員狀態
        cursor.execute(
            """
            UPDATE users
            SET is_verified = 1
            WHERE id = %s
            """,
            (user["id"],)
        )

        # 刪除已使用的驗證碼
        cursor.execute(
            """
            DELETE FROM email_verifications
            WHERE user_id = %s
            """,
            (user["id"],)
        )

        con.commit()

        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "message": "Email 驗證成功"
            }
        )

    except Exception:
        if con is not None:
            con.rollback()

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "message": "伺服器內部錯誤"
            }
        )

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()



@router.post("/api/resend-verification")
async def resend_verification(
    data: dict = Body(
        ...,
        examples=[
            {"email": "test@example.com"}
        ]
    )
):
    email = data.get("email")

    if not isinstance(email, str) or not email.strip():
        return JSONResponse(
            status_code=400,
            content={
                "ok": False,
                "message": "請輸入有效的 Email"
            }
        )

    email = email.strip().lower()

    con = None
    cursor = None

    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary=True)

        # 鎖定會員，避免同時重新寄送
        cursor.execute(
            """
            SELECT id, is_verified
            FROM users
            WHERE email = %s
            LIMIT 1
            FOR UPDATE
            """,
            (email,)
        )

        user = cursor.fetchone()

        # 避免透過 API 查詢哪些 Email 已註冊
        if user is None or user["is_verified"]:
            con.rollback()
            return JSONResponse(
                status_code=200,
                content={
                    "ok": True,
                    "message": "如果帳號需要驗證，新的驗證碼將會寄出"
                }
            )

        user_id = user["id"]

        cursor.execute(
            """
            SELECT last_sent_at
            FROM email_verifications
            WHERE user_id = %s
            FOR UPDATE
            """,
            (user_id,)
        )

        verification = cursor.fetchone()

        now = datetime.now(timezone.utc).replace(tzinfo=None)

        if verification is not None:
            # last_sent_at 由 MySQL 產生，使用資料庫的時區
            cursor.execute(
                "SELECT UTC_TIMESTAMP() AS utc_now"
            )
            db_utc_now = cursor.fetchone()["utc_now"]

            # 使用資料庫時間判斷冷卻期限
            cursor.execute(
                """
                SELECT TIMESTAMPDIFF(
                    SECOND,
                    last_sent_at,
                    NOW()
                ) AS elapsed_seconds
                FROM email_verifications
                WHERE user_id = %s
                """,
                (user_id,)
            )

            elapsed = cursor.fetchone()["elapsed_seconds"]

            if elapsed < RESEND_COOLDOWN_SECONDS:
                con.rollback()

                return JSONResponse(
                    status_code=429,
                    content={
                        "ok": False,
                        "message": "請稍後再重新取得驗證碼",
                        "retryAfter": RESEND_COOLDOWN_SECONDS - elapsed
                    }
                )

        code = generate_verification_code()
        code_hash = hash_verification_code(user_id, code)
        expires_at = get_expiration_time()

        if verification is not None:
            cursor.execute(
                """
                UPDATE email_verifications
                SET code_hash = %s,
                    expires_at = %s,
                    attempts = 0,
                    last_sent_at = NOW()
                WHERE user_id = %s
                """,
                (code_hash, expires_at, user_id)
            )
        else:
            cursor.execute(
                """
                INSERT INTO email_verifications
                (user_id, code_hash, expires_at, attempts, last_sent_at)
                VALUES (%s, %s, %s, 0, NOW())
                """,
                (user_id, code_hash, expires_at)
            )

        # 透過 Amazon SES 寄送新的驗證碼
        send_verification_email(email, code)

        # SES 接受寄送請求後，提交資料庫交易
        con.commit()

        return JSONResponse(
            status_code=200,
            content={
                "ok": True,
                "message": "新的驗證碼已產生，請查看開發終端機"
            }
        )

    except Exception:
        if con is not None:
            con.rollback()

        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "message": "伺服器內部錯誤"
            }
        )

    finally:
        if cursor is not None:
            cursor.close()

        if con is not None:
            con.close()

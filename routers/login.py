from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import json
from database import db_pool
from argon2 import PasswordHasher
from argon2.exceptions import (VerifyMismatchError, VerificationError)
from starlette.middleware.sessions import SessionMiddleware

router = APIRouter()
ph = PasswordHasher()

################################# 登陸的api ###########################################

## requirements: {"email": email, "password": password}  email是 username 或是 email (所以兩個都可以，用「或」來確認)

@router.post("/api/login")
async def login(request: Request):
    requirements = await request.json()
    email = requirements.get("email")
    password = requirements.get("password")
    sql = """
        SELECT id, password_hash, is_verified, status, email
        FROM users
        WHERE email = %s OR user_name = %s;
    """
    con = db_pool.get_connection()
    cursor = con.cursor(dictionary = True)
    print("已成功連線至資料庫")
    try:
        cursor.execute(sql, (email, email,))
        user = cursor.fetchone()
        if(user == None):
            print("帳號或密碼錯誤")
            return JSONResponse(
                status_code = 401,
                content = {"error": True, "message": "帳號或密碼錯誤", "inputError": True}
            )
        password_hash = user["password_hash"]
        user_id = user["id"]
        print(f"password_hash: {password_hash} \n id: {user_id}")
        try:
            ph.verify(password_hash, password)
            print("驗證成功")
        except(VerifyMismatchError, ValueError):
            return JSONResponse(
                status_code = 401,
                content = {"error": True, "message": "帳號或密碼錯誤","inputError": True}
            )
        print("驗證成功")
        if user["status"] != "active":
            return JSONResponse(
                status_code=403,
                content={
                    "ok": False,
                    "message": "此帳號目前無法登入"
                }
            )
        if not user["is_verified"]:
            return JSONResponse(
                status_code=403,
                content={
                    "ok": False,
                    "emailNotVerified": True,
                    "email": user["email"],
                    "message": "請先完成 Email 驗證"
                }
            )
        request.session["user_id"] = user_id

        return {
            "ok": True,
            "message": "登入成功"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content = {"error": True, "message": f"伺服器內部錯誤:{str(e)}"}
        )
    finally:
        cursor.close()
        con.close()
        print("資料庫連線已關閉")

################################# 登陸的api 結束 ###########################################
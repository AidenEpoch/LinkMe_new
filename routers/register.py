from fastapi import APIRouter, Request
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
async def register(request: Request):
    requirements = await request.json()
    sql = """
        INSERT INTO users(user_name, email, password_hash, display_name, avatar_url) VALUES(%s, %s, %s, %s, %s);
    """
    user_name = requirements.get("userName")
    email = requirements.get("email")
    password_hash = requirements.get("password")
    password_hash = ph.hash(password_hash)
    display_name = user_name
    avatar_url = "/static/image/avatar_default.png"
    con = db_pool.get_connection()
    cursor = con.cursor()
    print("已成功連線至資料庫")
    try:
        cursor.execute(sql, (user_name, email, password_hash, display_name, avatar_url,))
        con.commit()
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content = {"error": True, "message": f"伺服器內部錯誤: {str(e)}"}
        )
    finally:
        cursor.close()
        con.close()
    return {"ok": True}


############################### 註冊的api 結束 #######################################
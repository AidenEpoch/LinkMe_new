from fastapi import APIRouter, Request, Form
import json
from fastapi.responses import JSONResponse
from database import db_pool


router = APIRouter()

@router.patch("/api/edit/profile/bio")
async def editProfile(request:Request, text: str= Form()):
    user_id = request.session.get("user_id")
    if (user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    print(f"text: {text}")
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            UPDATE users SET bio = %s WHERE id = %s;
        """
        cursor.execute(sql, (text,user_id,))
        con.commit()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "is_edit": True}
        )
    except Exception as e: 
        return JSONResponse(
            status_code = 500,
            content = {"error": True, "message": f"伺服器錯誤: {str(e)}"}
        )
    finally:
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()


@router.patch("/api/edit/account/email")
async def editEmail(request: Request, email: str = Form()):
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
            UPDATE users SET email = %s WHERE id = %s;
        """
        cursor.execute(sql, (email, user_id,))
        con.commit()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已修改email"}
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



@router.get("/api/edit/account/privacy")
async def getPrivacy(request: Request):
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
            SELECT is_private FROM users WHERE id = %s;
        """
        cursor.execute(sql, (user_id,))
        is_private = cursor.fetchone()
        is_private = is_private["is_private"]
        print(f"is_private: {is_private}")
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已經取得隱私性的資訊", "is_private": is_private}
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


@router.patch("/api/edit/account/setPrivacy")
async def setAccountPrivacy(request: Request, privacy:bool = Form(...)):
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
            UPDATE users SET is_private = %s WHERE id = %s;
        """
        if(privacy):
            cursor.execute(sql, (1, user_id,))
        else:
            cursor.execute(sql, (0, user_id,))
        con.commit()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已經設定好帳號隱私性"}
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

@router.patch("/api/edit/displayName")
async def alterDisplayName(request: Request, display_name: str = Form(...)):
    user_id = request.session.get("user_id")
    if(user_id is None):
        return JSONResponse(
            status_code = 400,
            content = {"error"}
        )
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            UPDATE users SET display_name = %s WHERE id = %s;
        """
        cursor.execute(sql, (display_name, user_id,))
        con.commit()
        sql = """
            SELECT display_name FROM users WHERE id = %s;
        """
        cursor.execute(sql, (user_id,))
        user_data = cursor.fetchone()
        if user_data is None:
            return JSONResponse(
                status_code = 404,
                content = {"error": True, "message": "查無此用戶"}
            )
        user_displayName = user_data["display_name"]
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已成功更改顯示名稱", "display_name": user_displayName}
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
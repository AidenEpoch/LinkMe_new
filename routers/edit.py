from fastapi import APIRouter, Request
import json
from fastapi.responses import JSONResponse
from database import db_pool


router = APIRouter()

@router.patch("/api/edit")
async def editProfile(request:Request):
    user_id = request.session["user_id"]
    if (user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        
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
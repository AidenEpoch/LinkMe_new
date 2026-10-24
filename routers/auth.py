from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import json
from database import db_pool


router = APIRouter()

################################# session(使用者狀態)的api ############################################

@router.get("/api/auth")
async def getAuth(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    else:
        return {"ok": True, "message": "成功登入", "user_id": user_id}

################################# session的api 結束 ##################################################
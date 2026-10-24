from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import json
from database import db_pool

router = APIRouter()

#############################################  配對 api ##########################################

@router.post("/api/match")
async def linkUser(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    else:
        return
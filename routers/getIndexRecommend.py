from database import db_pool
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/api/getIndexRecommend")
async def getIndexRecommend(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 400,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    
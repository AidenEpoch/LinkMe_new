from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import json

router = APIRouter()

@router.post("/api/logout")
async def logout(request: Request):
    request.session.clear()
    return {"ok": True, "message": "成功登出"}
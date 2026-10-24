from fastapi import Request, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import json
from database import db_pool

router = APIRouter()

##############################################  各種頁面   ############################################################
@router.get("/")
async def index(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/login/login.html", media_type = "text/html")
    else:
        return FileResponse("./static/index/index.html", media_type = "text/html")

@router.get("/login")
async def loginPage(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/login/login.html", media_type = "text/html")




@router.get("/club")
async def getClubPage(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/login/login.html", media_type = "text/html")
    else:
        return FileResponse("./static/club/club.html", media_type = "text/html")
    return



@router.get("/linkme")
async def getLinkMePage(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/login/login.html", media_type = "text/html")
    else:
        return FileResponse("./static/linkme/linkme.html", media_type = "text/html")



@router.get("/search")
async def getSearchPage(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/login/login.html", media_type = "text/html")
    else:
        return FileResponse("./static/search/search.html", media_type = "text/html")

@router.get("/register")
async def getRegisterPage(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/register/register.html", media_type = "text/html")
    




@router.get("/{user_name}")
async def getMemberPage(request: Request, user_name: str):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/login/login.html", media_type = "text/html")
    else:
        return FileResponse("./static/user/user.html", media_type = "text/html")

####################################################################################################
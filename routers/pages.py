from fastapi import Request, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import json
from database import db_pool

router = APIRouter()

templates = Jinja2Templates(directory = "templates")

##############################################  各種頁面   ############################################################
@router.get("/")
async def index(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/login/login.html", media_type = "text/html")
    else:
        return templates.TemplateResponse(
            request = request,
            name = "index.html",
            context = {"user_id": user_id})

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
        return templates.TemplateResponse(
            request = request,
            name = "club.html",
            context = {"user_id": user_id}
        )



@router.get("/linkme/{userName}")
async def getLinkMePage(request: Request, userName: str):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/login/login.html", media_type = "text/html")
    else:
        return templates.TemplateResponse(
            request = request,
            name = "linkme.html",
            context = {"user_id": user_id}
        )



@router.get("/search")
async def getSearchPage(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/login/login.html", media_type = "text/html")
    else:
        return templates.TemplateResponse(
            request = request,
            name = "search.html",
            context = {"user_id": user_id}
        )

@router.get("/register")
async def getRegisterPage(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/register/register.html", media_type = "text/html")
    
@router.get("/edit")
async def goToEditPage(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/login/login.html", media_type = "text/html")
    return templates.TemplateResponse(
        request = request,
        name = "edit.html",
        context = {"user_id": user_id}
    )



@router.get("/{user_name}")
async def getMemberPage(request: Request, user_name: str):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return FileResponse("./static/login/login.html", media_type = "text/html")
    else:
        return templates.TemplateResponse(
            request = request,
            name = "user.html",
            context = {"user_id": user_id}
        )

####################################################################################################
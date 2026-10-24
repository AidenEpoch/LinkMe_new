from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import json
from argon2 import PasswordHasher
from argon2.exceptions import (VerifyMismatchError, VerificationError)
from starlette.middleware.sessions import SessionMiddleware
from database import db_pool
from routers import auth, login, pages, register, user, match, post
import os
from dotenv import load_dotenv
load_dotenv()

ph = PasswordHasher()

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key = os.environ["SECRET_KEY"],
    max_age = 60 * 60 * 24 * 28,
    https_only = False,
    same_site = "lax"
)



##############################################  各種頁面   ############################################################
app.include_router(pages.router)
################################################ 各種頁面結束   ####################################################



################################# 註冊的api ###########################################
app.include_router(register.router)
############################### 註冊的api 結束 #######################################



################################# 登陸的api ###########################################
app.include_router(login.router)
################################# 登陸的api 結束 ###########################################



################################# 貼文的api ###########################################

app.include_router(post.router)

############################### 貼文的 api 結束 ####################################


################################# session(使用者狀態)的api ############################################

app.include_router(auth.router)

################################# session的api 結束 ##################################################



################################ 取得 user 資訊的 api ################################################

app.include_router(user.router)

################################# 取得 user 資訊的 api 結束 #########################################

################################

app.include_router(match.router)



app.mount("/static", StaticFiles(directory = "static"))

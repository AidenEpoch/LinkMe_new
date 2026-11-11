from fastapi import *
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import json
from argon2 import PasswordHasher
from argon2.exceptions import (VerifyMismatchError, VerificationError)
from starlette.middleware.sessions import SessionMiddleware
from database import db_pool
from routers import auth, login, pages, register, user, match, post, logout, follow, link, indexPost, edit, search, indexFriendStatus, notify, linkmeuser, avatarUpload,postOp, chat, searchPost, postComment, club
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

###############################################  通知  #######################################################

app.include_router(notify.router)
##########################################################################################################


############################################### LinkMe 頁面 ##############################################

app.include_router(linkmeuser.router)

########################################################################################################


##############################################  聊天功能 ################################################

app.include_router(chat.router)

#####################################################################################################


###########################################  編輯  ##############################################################

app.include_router(edit.router)

##############################################################################################################


##############################################  追蹤   ############################################################
app.include_router(follow.router)
################################################ 追蹤結束   ####################################################


##############################################  首頁貼文   ############################################################
app.include_router(indexPost.router)

app.include_router(postOp.router)
################################################ 首頁貼文結束   ####################################################


################################# 註冊的api ###########################################
app.include_router(register.router)
############################### 註冊的api 結束 #######################################

##############################  搜尋的api #############################################

app.include_router(search.router)

############################ 搜尋的api結束 ############################################



################################# 登陸的api ###########################################
app.include_router(login.router)
################################# 登陸的api 結束 ###########################################


################################ 登出的 api ################################

app.include_router(logout.router)

############################### 登出的 api 結束 #######################


################################# 貼文的api ###########################################

app.include_router(post.router)

############################### 貼文的 api 結束 ####################################


################################# session(使用者狀態)的api ############################################

app.include_router(auth.router)

################################# session的api 結束 ##################################################



################################ 取得 user 資訊的 api ################################################

app.include_router(user.router)

app.include_router(indexFriendStatus.router)

################################# 取得 user 資訊的 api 結束 #########################################

################################ 搜尋頁面貼文 #####################################################

app.include_router(searchPost.router)

############################### 搜尋頁面貼文結束 ##################################################

app.include_router(match.router)

app.include_router(link.router)

app.include_router(avatarUpload.router)

app.include_router(postComment.router)

app.include_router(club.router)


app.mount("/static", StaticFiles(directory = "static"))

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import json
from database import db_pool

router = APIRouter()

################################ 取得 user 資訊的 api ################################################

@router.get("/api/user")
async def getUserInformation(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    else:
        sql = """
        SELECT user_name, display_name FROM users WHERE id = %s;
    """
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        print("已連線至資料庫")
        try:
            cursor.execute(sql, (user_id,))
            data = cursor.fetchone()
            user_name = data["user_name"]
            display_name = data["display_name"]
            returnData = dict()
            returnData["user_name"] = user_name
            returnData["display_name"] = display_name
            return JSONResponse(
                status_code = 200,
                content = {"ok": True, "data": returnData}
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



@router.get("/api/users/{user_name}")
async def getProfileInformation(request: Request, user_name: str):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    else:
        sql = """
            SELECT id, user_name, display_name FROM users WHERE user_name = %s;
        """
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        try:
            cursor.execute(sql, (user_name,))
            user = cursor.fetchone()
            if(user == None):
                return JSONResponse(
                    status_code = 404,
                    content = {"error": True, "message": "找不到這位使用者"}
                )
            is_owner = (user["id"] == int(user_id))
            return JSONResponse(
                status_code = 200,
                content = {"ok": True, 
                           "data": {
                               "user_name": user["user_name"],
                               "display_name": user["display_name"],
                               "is_owner": is_owner
                           }}
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

################################# 取得 user 資訊的 api 結束 #########################################
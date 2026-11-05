from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from database import db_pool

router = APIRouter()

@router.get("/api/searchResult")
async def getSearchResult(request: Request, keyword: str = Query(default = "", max_length = 300)):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    keyword = keyword.strip()
    if keyword == None:
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "data": []}
        )
    con = None
    cursor = None
    try:
        sql = """
            SELECT id, display_name, user_name FROM users WHERE display_name LIKE %s LIMIT 10;
        """
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        cursor.execute(sql, (f"%{keyword}%",))
        users = cursor.fetchall()
        sql = """
            SELECT avatar_url FROM users WHERE id = %s;
        """
        for user in users:
            cursor.execute(sql, (user["id"],))
            avatar_url = cursor.fetchone()
            user["avatar_url"] = avatar_url["avatar_url"]
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "data": users}
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
    
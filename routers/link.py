from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from database import db_pool


router = APIRouter()

@router.post("/api/linkme/skip/{user_name}")
async def linkMeSkip(request: Request, user_name: str):
    user_id = request.session.get("user_id")
    if(user_id is None):
        return JSONResponse(
            status_code = 400,
            content = {"error": True, "message": "尚未登入"}
        )
    try:
        con = None
        cursor = None
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            SELECT id FROM users WHERE user_name = %s;
        """
        cursor.execute(sql, (user_name,))
        matched_id = cursor.fetchone()
        matched_id = matched_id["id"]
        sql = """
            UPDATE matching_daily SET status = %s WHERE user_id = %s AND matched_user_id = %s;
        """
        cursor.execute(sql, ("skipped", user_id, matched_id,))
        con.commit()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已經拒絕此次配對"}
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


@router.get("/api/linkme/isSkip/{user_name}")
async def isSkip(request: Request, user_name: str):
    user_id = request.session.get("user_id")
    if(user_id is None):
        return JSONResponse(
            status_code = 400,
            content = {"error": True, "message": "尚未登入"}
        )
    try:
        con = None
        cursor = None
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            SELECT id FROM users WHERE user_name = %s;
        """
        cursor.execute(sql, (user_name,))
        matched_user = cursor.fetchone()

        if matched_user is None:
            return JSONResponse(
                status_code=404,
                content={"ok": False, "message": "找不到配對對象"}
            )

        matched_id = matched_user["id"]
        sql = """
            SELECT status FROM matching_daily WHERE user_id = %s AND matched_user_id = %s ORDER BY match_date DESC
            LIMIT 1;
        """
        cursor.execute(sql, (user_id, matched_id,))
        record = cursor.fetchone()

        skip = (record is not None and record["status"] == "skipped")
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "skip": skip}
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
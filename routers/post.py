import boto3
from fastapi import APIRouter, Request, File, Form, UploadFile
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import mysql.connector
import json
from database import db_pool
import uuid
import os


router = APIRouter()


s3_client = boto3.client("s3")
bucket_name = "linkmeproject"
cloudfront_name = "d32lm1ug1ggsp6.cloudfront.net"


@router.post("/api/postUpload")
async def postMessage(request: Request, text: str = Form(...), file: UploadFile = File(...)):
    user_id = request.session.get("user_id");
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    print(f"text: {text}")
    print(f"file: {file}")
    extension = os.path.splitext(file.filename or "")[1].lower()
    image_key = f"posts/{uuid.uuid4().hex}{extension}"
    sql = """
        SELECT user_name FROM users WHERE id = %s;
    """
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        print("已連線到資料庫")
        s3_client.upload_fileobj(
        file.file,
        bucket_name,
        image_key,
        ExtraArgs={"ContentType": file.content_type},
    )
        print(f"檔案已成功上傳至s3")
        img_url = f"https://{cloudfront_name}/{image_key}"
        print(f"img_url: {img_url}")
        print("目前到這裡(1)")
        cursor.execute(sql, (user_id,));
        print("目前到這裡(2)")
        data = cursor.fetchone()
        userName = data["user_name"]
        print(f"userName = {userName}")
        print(f"data: {data}")
        print("目前到這裡(3)")
        sql = """
            INSERT INTO posts(user_id, content, image_key) VALUES (%s, %s, %s);
        """
        cursor.execute(sql, (user_id, text, img_url,))
        con.commit()
        print("已成功將資料寫入 posts table")
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "data": userName, "message": "上傳成功"}
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
        print("資料庫已關閉")


@router.get("/api/userGetPost")
async def getMessage(request: Request):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 401,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
        SELECT content, image_key, created_at, id FROM posts WHERE user_id = %s ORDER BY created_at DESC, id DESC;
    """
        cursor.execute(sql, (user_id,))
        posts = cursor.fetchall()
        sql = """
        SELECT display_name FROM users WHERE id = %s;
    """
        cursor.execute(sql, (user_id,));
        name = cursor.fetchone()
        for post in posts:
            post["created_at"] = post["created_at"].isoformat()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "data": posts, "name": name}
        )
    except Exception as e:
        return JSONResponse(
            status_code = 500,
            content = {"error": True, "message": f"伺服器錯誤: {str(e)}"}
        )
    finally:
        if cursor is not None:
            cursor.close()
        if con is not None:
            con.close()
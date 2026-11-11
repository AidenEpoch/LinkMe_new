import boto3
from fastapi import APIRouter, Request, File, Form, UploadFile
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
import mysql.connector
import json
from database import db_pool
import uuid
import os


router = APIRouter()


s3_client = boto3.client("s3", region_name="us-east-1")
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
    con = None
    cursor = None
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
        print(f"img_key: {image_key}")
        cursor.execute(sql, (user_id,));
        data = cursor.fetchone()
        userName = data["user_name"]
        sql = """
            INSERT INTO posts(user_id, content, image_key) VALUES (%s, %s, %s);
        """
        cursor.execute(sql, (user_id, text, image_key,))
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
            if not post["image_key"]:
                post["image_url"] = None
            elif post["image_key"].startswith(("https://", "http://")):
                post["image_url"] = post["image_key"]
            else:
                post["image_url"] = f"https://{cloudfront_name}/{post['image_key']}"
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


@router.get("/api/GetPost/{user}")
async def getOthersPost(request: Request, user: str):
    user_id = request.session.get("user_id")
    print(f"收到的 user: {repr(user)}", flush=True)
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            SELECT id, display_name, is_private FROM users WHERE user_name = %s;
        """
        cursor.execute(sql, (user,))
        user_data = cursor.fetchone()
        if user_data is None:
            return JSONResponse(
                status_code = 404,
                content = {"error": True, "message": "查無此用戶"}
            )
        else:
            print(f"user:{user_data['id']}")
            sql = """
                SELECT content, image_key, created_at, id FROM posts WHERE user_id = %s ORDER BY created_at DESC, id DESC LIMIT 12;
            """
            userID = user_data["id"]
            name = user_data["display_name"]
            is_private = user_data["is_private"]
            is_owner = (user_data["id"] == int(user_id))
            cursor.execute(sql, (userID,))
            posts = cursor.fetchall()
            sql = """
                SELECT following_id FROM follows WHERE follower_id = %s AND following_id = %s;
            """
            cursor.execute(sql, (user_id, user_data["id"],))
            is_follow_list = cursor.fetchone()
            is_follow = True
            if(is_follow_list):
                is_follow = True
            else:
                is_follow = False
            for post in posts:
                post["created_at"] = post["created_at"].isoformat()
                if not post["image_key"]:
                    post["image_url"] = None
                elif post["image_key"].startswith(("https://", "http://")):
                    post["image_url"] = post["image_key"]
                else:
                    post["image_url"] = f"https://{cloudfront_name}/{post['image_key']}"
            canView = False
            if(is_owner == True):
                canView = True
            elif(is_private == False):
                canView = True
            elif(is_follow == True):
                canView = True
            return JSONResponse(
                status_code = 200,
                content = {"ok": True, "data": posts, "name": name, "is_private": is_private, "is_owner": is_owner, "is_follow": is_follow, "canView": canView}
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


@router.get("/api/showPost/{post_id}")
async def showPost(post_id: int, request: Request):
    userID = request.session.get("user_id")
    print(f"img_key = {post_id}")
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        sql = """
            SELECT content, user_id, image_key FROM posts WHERE id = %s;
        """
        cursor.execute(sql, (post_id,))
        postData = cursor.fetchone()
        if (postData == None):
            return JSONResponse(
                status_code = 404,
                content = {"error": True, "message": "查無此貼文"}
            )
        postContent = postData["content"]
        user_id = postData["user_id"]
        img_key = postData["image_key"]
        if not img_key:
            img_url = None
        elif img_key.startswith(("https://", "http://")):
            img_url = img_key
        else:
            img_url = f"https://{cloudfront_name}/{img_key}"
        sql = """
            SELECT display_name FROM users WHERE id = %s;
        """
        cursor.execute(sql, (user_id,))
        postName = cursor.fetchone()
        postName = postName["display_name"]
        sql = """
            SELECT * FROM post_like WHERE user_id = %s AND post_id = %s;
        """
        cursor.execute(sql, (userID, post_id,))
        like_data = cursor.fetchone()
        if(like_data):
            isLike = True
        else:
            isLike = False
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "content": postContent, "name": postName, "img_url": img_url, "isLike": isLike}
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
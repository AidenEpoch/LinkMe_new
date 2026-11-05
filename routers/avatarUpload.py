from database import db_pool
from fastapi import Request, APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
import uuid
import boto3
import json


router = APIRouter()
s3_client = boto3.client("s3", region_name="us-east-1")
bucket_name = "linkmeproject"
cloudfront_name = "d32lm1ug1ggsp6.cloudfront.net"

@router.post("/api/avatar/upload")
async def avatarUpload(request: Request, file: UploadFile = File(...)):
    user_id = request.session.get("user_id")
    if(user_id == None):
        return JSONResponse(
            status_code = 400,
            content = {"error": True, "message": "尚未登入"}
        )
    con = None
    cursor = None
    try:
        con = db_pool.get_connection()
        cursor = con.cursor(dictionary = True)
        print(f"已連線到資料庫")
        s3_key = f"avatars/{user_id}/{uuid.uuid4().hex}.jpg"
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            s3_key,
            ExtraArgs={"ContentType": "image/jpeg"}
        )
        avatar_url = f"https://{cloudfront_name}/{s3_key}"
        sql = """
            UPDATE users
            SET avatar_url = %s
            WHERE id = %s;
        """

        cursor.execute(sql, (avatar_url, user_id))
        if cursor.rowcount != 1:
            con.rollback()
            return JSONResponse(
                status_code=404,
                content={"error": True, "message": "找不到會員"}
            )

        con.commit()
        return JSONResponse(
            status_code = 200,
            content = {"ok": True, "message": "已成功上傳大頭貼", "avatar_url": avatar_url}
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

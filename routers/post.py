import boto3
from fastapi import APIRouter, Request, File, Form, UploadFile
import mysql.connector
import json
from database import db_pool


router = APIRouter()


s3_client = boto3.client("s3")
bucket_name = "linkmeproject"
cloudfront_name = "d32lm1ug1ggsp6.cloudfront.net"


@router.post("/api/postUpload")
async def postMessage(text: str = Form(...), file: UploadFile = File(...)):
    print(f"text: {text}")
    print(f"file: {file}")
    s3_client.upload_fileobj(
        file.file,
        bucket_name,
        file.filename,
        ExtraArgs={"ContentType": file.content_type},
    )
    print(f"檔案已成功上傳至s3")
    return


@router.get("/api/postGet")
async def getMessage():
    return
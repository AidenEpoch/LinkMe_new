
import boto3
from botocore.exceptions import ClientError

# Amazon SES 所在區域
AWS_REGION = "us-east-1"

# 替換成你在 SES 已驗證的 Email
SENDER_EMAIL = "roger.sly.sky@gmail.com"

ses_client = boto3.client(
    "ses",
    region_name=AWS_REGION
)


def send_verification_email(receiver_email, code):

    subject = "LinkMe - 電子郵件驗證碼"

    body_text = f"""
歡迎加入 LinkMe！

你的電子郵件驗證碼為：

{code}

此驗證碼將在 10 分鐘後失效。

如果你沒有註冊 LinkMe，請忽略這封郵件。

LinkMe Team
"""

    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={
                "ToAddresses": [receiver_email]
            },
            Message={
                "Subject": {
                    "Data": subject,
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Text": {
                        "Data": body_text,
                        "Charset": "UTF-8"
                    }
                }
            }
        )

        return response["MessageId"]

    except ClientError as error:
        print(
            "SES 寄送失敗：",
            error.response["Error"]["Code"]
        )
        raise

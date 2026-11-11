
from email_sender import send_verification_email

receiver_email = "roger.sly.sky@gmail.com"

message_id = send_verification_email(
    receiver_email,
    "123456"
)

print("SES 寄送成功！")
print("Message ID:", message_id)

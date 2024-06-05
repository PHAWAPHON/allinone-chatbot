import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ขอบเขตสำหรับการส่งอีเมล
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def create_message(sender, to, cc, subject, message_text):
    message = MIMEMultipart()
    message['to'] = to
    message['cc'] = cc
    message['from'] = sender
    message['subject'] = subject

    # ตั้งค่าความสำคัญของอีเมล
    message['X-Priority'] = '1'  # ค่าที่ต่ำที่สุดคือ 1 (สูงสุด), 5 คือต่ำสุด
    message['Importance'] = 'high'
    message['X-MSMail-Priority'] = 'High'

    message.attach(MIMEText(message_text, 'plain'))
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_message(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f'รหัสข้อความ: {message["id"]}')
        return message
    except Exception as error:
        print(f'เกิดข้อผิดพลาด: {error}')

def get_credentials():
    creds = None

    # ตรวจสอบว่า token2.json มีอยู่เพื่อโหลดข้อมูลรับรองที่บันทึกไว้ก่อนหน้า
    if os.path.exists('token2.json'):
        creds = Credentials.from_authorized_user_file('token2.json', SCOPES)

    # ถ้าข้อมูลรับรองไม่พร้อมใช้งานหรือไม่ถูกต้อง ให้รับข้อมูลรับรองใหม่
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f'เกิดข้อผิดพลาดขณะรีเฟรชโทเค็น: {e}')
                creds = None  # เพื่อให้ไปทำการรับรองความถูกต้องใหม่
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'E:\Project\flask-sql-example-main\src\views\client_secret_229484673590-kh1m864t652u3gduprv1opualj3l8i6k.apps.googleusercontent.com.json', SCOPES)
            creds = flow.run_local_server(port=8080, access_type='offline')

        if creds and creds.refresh_token:
            print("Refresh token obtained.")
        else:
            print("No refresh token found.")

        # บันทึกข้อมูลรับรองสำหรับใช้งานในอนาคต
        with open('token2.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def main():
    creds = get_credentials()

    # สร้างบริการ API ของ Gmail
    service = build('gmail', 'v1', credentials=creds)

    sender = "allinonesendingemail@gmail.com"
    to = "chanchon1150@gmail.com"
    cc = "misternarn@gmail.com"  # เพิ่มผู้รับในช่อง cc
    subject = "Test email"
    message_text = "This is a test email sent from the Gmail API with CC. โหลๆๆๆเทสสๆๆ ส่งจาก gmail api"

    message = create_message(sender, to, cc, subject, message_text)
    send_message(service, "me", message)

if __name__ == '__main__':
    main()

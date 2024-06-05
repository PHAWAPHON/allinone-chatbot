from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SERVICE_ACCOUNT_FILE = r'E:\Project\flask-sql-example-main\src\views\secret\linebot-424114-449b9888be1d.json'
CHUNK_SIZE = 1024 * 1024 * 10

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/drive']
)
drive_service = build('drive', 'v3', credentials=credentials)

file_metadata = {
    'name': 'IMG_9811.png',
    'parents': ['1kzB_6Gj2JKU6yjym_xVqt2GGTyBoSsRW']
}
file_path = r'E:\Project\flask-sql-example-main\uploads\IMG_9811.png'
mime_type = 'image/png'

media = MediaFileUpload(file_path, mimetype=mime_type, chunksize=CHUNK_SIZE, resumable=True)
request = drive_service.files().create(body=file_metadata, media_body=media, fields='id')

response = None
while response is None:
    status, response = request.next_chunk()
    if status:
        print(f"Uploaded {int(status.progress() * 100)}%")

file_id = response.get('id')
print(f"File ID: {file_id}")

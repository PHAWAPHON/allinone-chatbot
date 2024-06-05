import json
import os
import pika
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
from ..models import db, File

SERVICE_ACCOUNT_FILE = r'E:\Project\flask-sql-example-main\src\views\secret\linebot-424114-449b9888be1d.json'
CHUNK_SIZE = 1024 * 1024 * 10

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/drive']
)
drive_service = build('drive', 'v3', credentials=credentials)

print("Connecting to RabbitMQ...")  # Log to indicate consumer is starting
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
print("Connected to RabbitMQ.")

channel.queue_declare(queue='file_uploads')

def get_drive_folder_ids(file_id):
    try:
        file_settings = db.session.query(File).filter_by(id=file_id).first()
        if file_settings:
            return (
                file_settings.GDRIVE_FOLDER_ID,
                file_settings.GDRIVE_FOLDER_IMAGE_ID,
                file_settings.GDRIVE_FOLDER_VIDEO_ID,
                file_settings.GDRIVE_FOLDER_AUDIO_ID
            )
        else:
            return None, None, None, None
    except Exception as e:
        print(f"Error fetching file settings: {e}")
        return None, None, None, None

def get_folder_id_by_mime_type(mime_type, customer_id):
    gdrive_folder_id, gdrive_folder_image_id, gdrive_folder_video_id, gdrive_folder_audio_id = get_drive_folder_ids(customer_id)
    if mime_type.startswith('image/'):
        return gdrive_folder_image_id
    elif mime_type.startswith('video/'):
        return gdrive_folder_video_id
    elif mime_type.startswith('audio/'):
        return gdrive_folder_audio_id
    else:
        return gdrive_folder_id

def upload_to_drive(file_path, mime_type, file_name, gdrive_folder_id):
    try:
        print(f"Uploading file: {file_name} to folder: {gdrive_folder_id}")
        print(f"File path: {file_path}, Mime type: {mime_type}")

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None

        file_metadata = {
            'name': file_name,
            'parents': [gdrive_folder_id]
        }
        print(f"File metadata: {file_metadata}")
        media = MediaFileUpload(file_path, mimetype=mime_type, chunksize=CHUNK_SIZE, resumable=True)
        print(f"MediaFileUpload object created")
        request = drive_service.files().create(body=file_metadata, media_body=media, fields='id')
        print(f"Request object: {request}")

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}% of {file_name}")

        file_id = response.get('id')
        print(f"File ID: {file_id}")
        os.remove(file_path)
        return f'https://drive.google.com/uc?id={file_id}'
    except Exception as error:
        print(f"Error uploading to Google Drive: {error}")
        return None

def callback(ch, method, properties, body):
    try:
        print(f" [x] Received message")
        message = json.loads(body)
        print(f"Message content: {message}")
        file_path = message['file_path']
        mime_type = message['mime_type']
        file_name = message['file_name']
        customer_id = message['customer_id']

        print(f" [x] Received upload request for: {file_name} with path: {file_path}")

        gdrive_folder_id = get_folder_id_by_mime_type(mime_type, customer_id)
        print(f"gdrive_folder_id: {gdrive_folder_id}")
        if gdrive_folder_id:
            upload_url = upload_to_drive(file_path, mime_type, file_name, gdrive_folder_id)
            if upload_url:
                print(f'File uploaded successfully: {upload_url}')
            else:
                print(f'Failed to upload file: {file_name}')
        else:
            print(f'No appropriate Google Drive folder found for file: {file_name}')
    except Exception as e:
        print(f"Error processing message: {e}")

channel.basic_consume(queue='file_uploads', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

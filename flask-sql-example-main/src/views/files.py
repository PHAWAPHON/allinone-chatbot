import os
import json
import pika
from flask import Blueprint, jsonify, request, render_template
from werkzeug.utils import secure_filename
from ..models import db, File

bp = Blueprint("files", __name__, url_prefix="/files")

def send_upload_request(file_path, mime_type, file_name, customer_id):
    try:
        print(f"Connecting to RabbitMQ to send upload request for: {file_name}")
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        print("Connected to RabbitMQ.")

        channel.queue_declare(queue='file_uploads')

        message = json.dumps({
            'file_path': file_path,
            'mime_type': mime_type,
            'file_name': file_name,
            'customer_id': customer_id
        })

        channel.basic_publish(exchange='', routing_key='file_uploads', body=message)
        print(f" [x] Sent upload request for: {file_name}")
        connection.close()
    except Exception as e:
        print(f"Error sending upload request: {e}")

def get_drive_folder_ids(file_id):
    try:
        print(f"Received file_id: {file_id}")
        file_settings = db.session.query(File).filter_by(id=file_id).first()
        if file_settings:
            print(f"Fetched file settings: {file_settings.GDRIVE_FOLDER_IMAGE_ID}, {file_settings.GDRIVE_FOLDER_VIDEO_ID}, {file_settings.GDRIVE_FOLDER_AUDIO_ID}")
            return (
                file_settings.GDRIVE_FOLDER_ID,
                file_settings.GDRIVE_FOLDER_IMAGE_ID,
                file_settings.GDRIVE_FOLDER_VIDEO_ID,
                file_settings.GDRIVE_FOLDER_AUDIO_ID
            )
        else:
            print("No file settings found for the given file_id")
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

@bp.route('/upload', methods=['POST'])
def upload_files():
    if request.method == 'POST':
        if not os.path.exists('uploads'):
            os.makedirs('uploads')

        files = request.files.getlist('files[]')
        customer_id = request.form.get('customer_id')
        upload_results = []

        for file in files:
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join('uploads', filename)

                with open(file_path, 'wb') as f:
                    f.write(file.read())

                mime_type = get_mime_type(filename.split('.').pop().lower())
                gdrive_folder_id = get_folder_id_by_mime_type(mime_type, customer_id)
                
                if gdrive_folder_id is None:
                    upload_results.append({'filename': filename, 'url': None, 'error': 'No appropriate Google Drive folder found'})
                    continue
                send_upload_request(file_path, mime_type, filename, customer_id)
                upload_results.append({'filename': filename, 'status': 'Queued for upload'})

        return jsonify({'status': 'success', 'message': 'Files processed', 'results': upload_results})

    return jsonify({'status': 'error', 'message': 'Invalid request method'})

@bp.route('/', methods=['GET'])
def index():
    customer_id = request.args.get('customer_id')
    return render_template('index.html.jinja', customer_id=customer_id)

def get_mime_type(file_type):
    mime_types = {
        "pdf": "application/pdf",
        "zip": "application/zip",
        "rar": "application/vnd.rar",
        "7z": "application/x-7z-compressed",
        "doc": "application/msword",
        "xls": "application/vnd.ms-excel",
        "ppt": "application/vnd.ms-powerpoint",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "mp4": "video/mp4",
        "mp3": "audio/mpeg",
        "m4a": "audio/mp4",
        "png": "image/png",
        "gif": "image/gif",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "txt": "text/plain",
        "svg": "image/svg+xml",
        "avi": "video/x-msvideo",
        "mov": "video/quicktime",
        "flv": "video/x-flv",
        "wmv": "video/x-ms-wmv",
        "mkv": "video/x-matroska",
        "ogg": "audio/ogg",
        "wav": "audio/wav",
        "json": "application/json",
    }
    return mime_types.get(file_type, "undefined")

def extract_filename_from_url(url):
    return url.split('/')[-1]

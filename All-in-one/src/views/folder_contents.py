from flask import Blueprint, jsonify, request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from ..models import db, File
import logging
import redis

bp = Blueprint("files_content", __name__, url_prefix="/files_contents")

SERVICE_ACCOUNT_FILE = r'E:\Project\flask-sql-example-main\src\views\secret\linebot-424114-449b9888be1d.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/drive']
)
drive_service = build('drive', 'v3', credentials=credentials)

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

MAX_BUBBLES = 10  

def list_files_in_folder(folder_id, page_token=None):
    results = drive_service.files().list(
        q=f"'{folder_id}' in parents",
        spaces='drive',
        fields='nextPageToken, files(id, name, mimeType, webViewLink, thumbnailLink)',
        pageSize=MAX_BUBBLES,
        pageToken=page_token
    ).execute()
    
    return results.get('files', []), results.get('nextPageToken')

def get_file_settings(customer_id):
    return db.session.query(File).filter_by(id=customer_id).first()

def fetch_files_by_type(folder_id, mime_type_prefix, page_token=None):
    files, next_page_token = list_files_in_folder(folder_id, page_token)
    filtered_files = []
    for file in files:
        if file['mimeType'].startswith(mime_type_prefix):
            file_info = {
                'id': file['id'],
                'name': file['name'],
                'web_view_link': file['webViewLink'],
                'thumbnail_link': file.get('thumbnailLink')
            }
            filtered_files.append(file_info)
    return filtered_files, next_page_token

def format_room_flex(data, type_label):
    bubble_list = []
    placeholder_image = "https://example.com/placeholder-image.jpg"  # Placeholder image URL
    for item in data:
        html_link = item.get('web_view_link', 'https://calendar.google.com')
        hero_url = item.get('thumbnail_link') or placeholder_image
        
        hero_content = {
            "type": "image",
            "url": hero_url,
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        }
        
        if type_label in ['videos', 'audios'] and not item.get('thumbnail_link'):
            hero_content = {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": item['name'],
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True
                    }
                ]
            }

        bubble = {
            "type": "bubble",
            "hero": hero_content,
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": item['name'],
                        "weight": "bold",
                        "size": "xl",
                        "wrap": True
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "More Info",
                            "uri": html_link
                        }
                    }
                ],
                "flex": 0
            }
        }
        bubble_list.append(bubble)
    carousel = {
        "type": "carousel",
        "contents": bubble_list
    }
    return carousel

def botnoipayload(flexdata, next_page_token=None):
    payload = {
        "response_type": "object",
        "line_payload": [{
            "type": "flex",
            "altText": "Files",
            "contents": flexdata
        }]
    }
    if next_page_token:
        payload["next_page_token"] = next_page_token
    return payload

@bp.route('/folder/<customer_id>/images', methods=['GET'])
def get_images(customer_id):
    page_token = request.args.get('page_token', None)
    reset_token = request.args.get('reset_token', 'false').lower() == 'true'
    redis_key = f'{customer_id}_images_next_page_token'
    
    try:
        file_settings = get_file_settings(customer_id)
        if not file_settings:
            return jsonify({'status': 'error', 'message': 'No settings found for the given customer ID'})

        parent_folder_id = file_settings.GDRIVE_FOLDER_IMAGE_ID
        if not parent_folder_id:
            return jsonify({'status': 'error', 'message': 'No folder ID found for the given customer ID'})

        if reset_token:
            redis_client.delete(redis_key)

        if not page_token:
            page_token = redis_client.get(redis_key)
            if page_token:
                page_token = page_token.decode('utf-8')

        images, next_page_token = fetch_files_by_type(parent_folder_id, 'image/', page_token)
        line_payload = format_room_flex(images, 'images')
        
        if next_page_token:
            redis_client.set(redis_key, next_page_token)
        
        return jsonify(botnoipayload(line_payload, next_page_token))
    except Exception as error:
        logging.error(f"Error retrieving image files: {error}")
        return jsonify({'status': 'error', 'message': str(error)})

@bp.route('/folder/<customer_id>/videos', methods=['GET'])
def get_videos(customer_id):
    page_token = request.args.get('page_token', None)
    reset_token = request.args.get('reset_token', 'false').lower() == 'true'
    redis_key = f'{customer_id}_videos_next_page_token'
    
    try:
        file_settings = get_file_settings(customer_id)
        if not file_settings:
            return jsonify({'status': 'error', 'message': 'No settings found for the given customer ID'})

        parent_folder_id = file_settings.GDRIVE_FOLDER_VIDEO_ID
        if not parent_folder_id:
            return jsonify({'status': 'error', 'message': 'No folder ID found for the given customer ID'})

        if reset_token:
            redis_client.delete(redis_key)

        if not page_token:
            page_token = redis_client.get(redis_key)
            if page_token:
                page_token = page_token.decode('utf-8')

        videos, next_page_token = fetch_files_by_type(parent_folder_id, 'video/', page_token)
        line_payload = format_room_flex(videos, 'videos')
        
        if next_page_token:
            redis_client.set(redis_key, next_page_token)
        
        return jsonify(botnoipayload(line_payload, next_page_token))
    except Exception as error:
        logging.error(f"Error retrieving video files: {error}")
        return jsonify({'status': 'error', 'message': str(error)})

@bp.route('/folder/<customer_id>/audios', methods=['GET'])
def get_audios(customer_id):
    page_token = request.args.get('page_token', None)
    reset_token = request.args.get('reset_token', 'false').lower() == 'true'
    redis_key = f'{customer_id}_audios_next_page_token'
    
    try:
        file_settings = get_file_settings(customer_id)
        if not file_settings:
            return jsonify({'status': 'error', 'message': 'No settings found for the given customer ID'})

        parent_folder_id = file_settings.GDRIVE_FOLDER_AUDIO_ID
        if not parent_folder_id:
            return jsonify({'status': 'error', 'message': 'No folder ID found for the given customer ID'})

        if reset_token:
            redis_client.delete(redis_key)

        if not page_token:
            page_token = redis_client.get(redis_key)
            if page_token:
                page_token = page_token.decode('utf-8')

        audios, next_page_token = fetch_files_by_type(parent_folder_id, 'audio/', page_token)
        line_payload = format_room_flex(audios, 'audios')
       
        if next_page_token:
            redis_client.set(redis_key, next_page_token)
        
        return jsonify(botnoipayload(line_payload, next_page_token))
    except Exception as error:
        logging.error(f"Error retrieving audio files: {error}")
        return jsonify({'status': 'error', 'message': str(error)})

@bp.route('/reset_token/<customer_id>', methods=['POST'])
def reset_token(customer_id):
    try:
        redis_client.delete(f'{customer_id}_images_next_page_token')
        redis_client.delete(f'{customer_id}_videos_next_page_token')
        redis_client.delete(f'{customer_id}_audios_next_page_token')
        return jsonify({'status': 'success', 'message': 'Page tokens reset successfully'})
    except Exception as error:
        logging.error(f"Error resetting page tokens: {error}")
        return jsonify({'status': 'error', 'message': str(error)})

def extract_filename_from_url(url):
    return url.split('/')[-1]

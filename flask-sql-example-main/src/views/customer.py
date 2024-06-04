from flask import Blueprint, jsonify, request, json
from ..models import db, File, GoogleCalendar, GoogleForm
import re
from src.flex_message_utils import format_room_flex, botnoipayload
from cryptography.fernet import Fernet
import base64
bp = Blueprint("customer", __name__, url_prefix="/customer")



def generate_key_and_encrypt(data):
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data.encode())
    return key, encrypted_data


def decrypt_data(data, key):
    cipher = Fernet(key)
    return cipher.decrypt(data).decode()

def extract_id(url):
    match = re.search(r'/folders/([a-zA-Z0-9-_]+)', url)
    if match:
        return match.group(1)
    return url

@bp.route('/insert_or_get_customer', methods=['POST'])
def insert_or_get_customer():
    data = request.data
    data2 = json.loads(data)
    print(data2)
    if not data2 or 'id' not in data2:
        return jsonify({'status': 'error', 'message': 'Invalid input'})

    customer_id = data2['id']
    customer = File.query.filter_by(id=customer_id).first()
    customer_drive_id = GoogleCalendar.query.filter_by(id=customer_id).first()
    customer_forms_id = GoogleForm.query.filter_by(id=customer_id).first()
    if customer or customer_drive_id:
        return jsonify({'status': 'success', 'message': 'Customer already exists', 'customer_id': customer.id})
    else:
        customer = File(id=customer_id)
        customer_drive_id = GoogleCalendar(id=customer_id)
        customer_forms_id = GoogleForm(id=customer_id)
        db.session.add(customer_drive_id)
        db.session.add(customer)
        db.session.add(customer_forms_id)
        db.session.commit()
        event_data = [{
            'date': '2023-06-01',
            'time': '10:00',
            'summary': f'Customer ID: {customer.id}',
            'location': 'No Location',
            'description': 'New customer added successfully.'
        }]
        flex_message = format_room_flex(event_data)
        response_payload = botnoipayload(flex_message)
        
        return jsonify(response_payload)

@bp.route('/insert_customer_all', methods=['POST'])
def insert_customer_all():
    data = request.data
    data2 = json.loads(data)
    print(data2)
    if not data2 or 'id' not in data2:
        return jsonify({'status': 'error', 'message': 'Invalid input'})

    customer_id = data2['id']
    customer_gdrive_id = extract_id(data2['GDRIVE_FOLDER_ID'])
    customer_gimage_id = extract_id(data2['GDRIVE_FOLDER_IMAGE_ID'])
    customer_gvideo_id = extract_id(data2['GDRIVE_FOLDER_VIDEO_ID'])
    customer_gaudio_id = extract_id(data2['GDRIVE_FOLDER_AUDIO_ID'])
    customer = File(id=customer_id, GDRIVE_FOLDER_ID=customer_gdrive_id, GDRIVE_FOLDER_IMAGE_ID=customer_gimage_id, GDRIVE_FOLDER_VIDEO_ID=customer_gvideo_id, GDRIVE_FOLDER_AUDIO_ID=customer_gaudio_id)
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Customer added successfully', 'customer_id': customer.id})

@bp.route('/insert_folder_id', methods=['POST'])
def insert_folder_id():
    data = request.data
    data2 = json.loads(data)
    print(data2)
    if not data2 or 'id' not in data2 or 'GDRIVE_FOLDER_ID' not in data2:
        return jsonify({'status': 'error', 'message': 'Invalid input'})

    customer_id = data2['id']
    customer_gdrive_id = extract_id(data2['GDRIVE_FOLDER_ID'])
    customer = db.session.query(File).filter_by(id=customer_id).first()
    if customer:
        customer.GDRIVE_FOLDER_ID = customer_gdrive_id
    else:
        customer = File(id=customer_id, GDRIVE_FOLDER_ID=customer_gdrive_id)
        db.session.add(customer)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Folder ID added/updated successfully', 'customer_id': customer.id}), 201

@bp.route('/insert_image_id', methods=['POST'])
def insert_image_id():
    data = request.data
    data2 = json.loads(data)
    print(data2)
    if not data2 or 'id' not in data2 or 'GDRIVE_FOLDER_IMAGE_ID' not in data2:
        return jsonify({'status': 'error', 'message': 'Invalid input'})

    customer_id = data2['id']
    customer_gimage_id = extract_id(data2['GDRIVE_FOLDER_IMAGE_ID'])
    customer = db.session.query(File).filter_by(id=customer_id).first()
    if customer:
        customer.GDRIVE_FOLDER_IMAGE_ID = customer_gimage_id
    else:
        customer = File(id=customer_id, GDRIVE_FOLDER_IMAGE_ID=customer_gimage_id)
        db.session.add(customer)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Image ID added/updated successfully', 'customer_id': customer.id})

@bp.route('/insert_video_id', methods=['POST'])
def insert_video_id():
    data = request.data
    data2 = json.loads(data)
    print(data2)
    if not data2 or 'id' not in data2 or 'GDRIVE_FOLDER_VIDEO_ID' not in data2:
        return jsonify({'status': 'error', 'message': 'Invalid input'})

    customer_id = data2['id']
    customer_gvideo_id = extract_id(data2['GDRIVE_FOLDER_VIDEO_ID'])
    customer = db.session.query(File).filter_by(id=customer_id).first()
    if customer:
        customer.GDRIVE_FOLDER_VIDEO_ID = customer_gvideo_id
    else:
        customer = File(id=customer_id, GDRIVE_FOLDER_VIDEO_ID=customer_gvideo_id)
        db.session.add(customer)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Video ID added/updated successfully', 'customer_id': customer.id})

@bp.route('/insert_audio_id', methods=['POST'])
def insert_audio_id():
    data = request.data
    data2 = json.loads(data)
    print(data2)
    if not data2 or 'id' not in data2 or 'GDRIVE_FOLDER_AUDIO_ID' not in data2:
        return jsonify({'status': 'error', 'message': 'Invalid input'})

    customer_id = data2['id']
    customer_gaudio_id = extract_id(data2['GDRIVE_FOLDER_AUDIO_ID'])
    customer = db.session.query(File).filter_by(id=customer_id).first()
    if customer:
        customer.GDRIVE_FOLDER_AUDIO_ID = customer_gaudio_id
    else:
        customer = File(id=customer_id, GDRIVE_FOLDER_AUDIO_ID=customer_gaudio_id)
        db.session.add(customer)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Audio ID added/updated successfully', 'customer_id': customer.id})


@bp.route('/insert_google_calendar_id', methods=['POST'])
def insert_google_calendar_id():
    data = request.data
    data2 = json.loads(data)
    print(data2)
    if not data2 or 'id' not in data2 or 'calendar_id' not in data2:
        return jsonify({'status': 'error', 'message': 'Invalid input'})

    customer_id = data2['id']
    calendar_id = data2['calendar_id']
    
    encryption_key, encrypted_calendar_id = generate_key_and_encrypt(calendar_id)
    encrypted_calendar_id = encrypted_calendar_id.decode() 
    encryption_key = encryption_key.decode()  
    
    print(f"Customer ID: {customer_id}, Encrypted Calendar ID: {encrypted_calendar_id}, Key: {encryption_key}")
    
    customer = db.session.query(GoogleCalendar).filter_by(id=customer_id).first()
    if customer:
        customer.calendar_id = encrypted_calendar_id
        customer.key = encryption_key
    else:
        customer = GoogleCalendar(id=customer_id, calendar_id=encrypted_calendar_id, key=encryption_key)
        db.session.add(customer)
        
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Google Calendar ID added/updated successfully', 'customer_id': customer.id})
    

from flask import Flask, request, jsonify, Blueprint, json
from google.oauth2 import service_account
from googleapiclient.discovery import build
import redis
import pytz
import datetime as dt
from ..payload import create_form_success_message, format_data, format_room_flex, botnoipayload
from ..models import db, GoogleForm

SCOPES = ['https://www.googleapis.com/auth/forms.responses.readonly', 'https://www.googleapis.com/auth/forms', 'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = r'E:\Project\flask-sql-example-main\src\views\secret\linebot-g-forms.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

forms_service = build('forms', 'v1', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)

bp = Blueprint("forms", __name__, url_prefix="/forms")

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def create_google_form(title, description, questions):
    form = {
        "info": {
            "title": title
        }
    }

    result = forms_service.forms().create(body=form).execute()
    form_id = result['formId']
    edit_form_link = f"https://docs.google.com/forms/d/{form_id}/edit"
    view_form_link = f"https://docs.google.com/forms/d/{form_id}/viewform"
    
    update_requests = [
        {
            "updateFormInfo": {
                "info": {
                    "description": description
                },
                "updateMask": "description"
            }
        }
    ]
    index = 0
    for question in questions:
        update_requests.append({
            "createItem": {
                "item": {
                    "title": question['title'],
                    "questionItem": {
                        "question": {
                            "required": question.get('required', False),
                            "textQuestion": {
                                "paragraph": question.get('paragraph', False)
                            }
                        }
                    }
                },
                "location": {
                    "index": index
                }
            }
        })
        index += 1  

    forms_service.forms().batchUpdate(formId=form_id, body={"requests": update_requests}).execute()
    
    return form_id, view_form_link, edit_form_link

def share_form_with_email(form_id, email):
    drive_file_id = form_id
    permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': email
    }

    drive_service.permissions().create(
        fileId=drive_file_id,
        body=permission,
        fields='id',
    ).execute()

def get_form_responses(form_id):
    try:
        responses = forms_service.forms().responses().list(formId=form_id).execute()
        print(f"API Response: {responses}")
        return responses
    except Exception as e:
        print(f"Error fetching form responses: {e}")
        return {}

def get_form_location(form_id):
    file_metadata = drive_service.files().get(fileId=form_id, fields="id, name, mimeType, parents, webViewLink").execute()
    return file_metadata

@bp.route('/add-question', methods=['POST'])
def add_question():
    data = request.data
    info = json.loads(data)
    question = info.get('question')
    if question:
        redis_client.rpush('questions', json.dumps(question))
        return jsonify({'status': 'Question added'})
    return jsonify({'error': 'No question provided'})

@bp.route('/create-form', methods=['POST'])
def create_form():
    data = request.data
    data = json.loads(data)
    customer_id = data.get('id')
    title = data.get('title')
    description = data.get('description')
    email = data.get('email')
    
    if not customer_id: 
        return jsonify({'error': 'Invalid customer ID'}), 400

    existing_form = db.session.query(GoogleForm).filter_by(id=customer_id).first()
    
    questions = [json.loads(q) for q in redis_client.lrange('questions', 0, -1)]
    form_id, view_form_link, edit_form_link = create_google_form(title, description, questions)
    
    if email:
        share_form_with_email(form_id, email)
    
    form_metadata = get_form_location(form_id)
    
    if existing_form:
        existing_form.form_id = view_form_link
        existing_form.edit_form_link = edit_form_link
    else:
        new_form = GoogleForm(id=customer_id, form_id=view_form_link, edit_form_link=edit_form_link)
        db.session.add(new_form)
    
    db.session.commit()
    
    redis_client.delete('questions')
    
    print({'form_link': view_form_link, 'form_id': form_id, 'edit_form_link': edit_form_link, 'customer_id': customer_id})
    return jsonify({'form_link': view_form_link, 'form_id': form_id, 'edit_form_link': edit_form_link, 'customer_id': customer_id})

@bp.route('/get-form-responses', methods=['POST'])
def get_responses():
    data = request.data
    customer_id = json.loads(data)
    customer_id = customer_id.get('id')
    form_entry = db.session.query(GoogleForm).filter_by(id=customer_id).first()
    
    if form_entry is None:
        return jsonify({'error': 'Form not found for the provided customer ID'})
    
    form_id = form_entry.form_id
    print(f"Form ID: {form_id}")
    return jsonify({'responses': form_id})

@bp.route('/get-form-location', methods=['POST'])
def get_location():
    data = request.data
    customer_id = json.loads(data)
    customer_id = customer_id.get('id')
    form_entry = db.session.query(GoogleForm).filter_by(id=customer_id).first()
    
    if form_entry is None:
        return jsonify({'error': 'Form not found for the provided customer ID'})
    
    form_id = form_entry.edit_form_link
    print(f"Form ID: {form_id}")
    
    print(f"Form ID: {form_id}")
    return jsonify({'responses': form_id})


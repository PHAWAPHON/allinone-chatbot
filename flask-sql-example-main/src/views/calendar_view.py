import os.path
import datetime as dt
from flask import Blueprint, jsonify, request, json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
from cryptography.fernet import Fernet
from ..models import db, GoogleCalendar
from src.flex_message_utils import format_data, format_room_flex, botnoipayload, create_reminder_selection_bubble

bp = Blueprint("calendar_bp", __name__, url_prefix="/")

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def decrypt_data(data, key):
    cipher = Fernet(key)
    return cipher.decrypt(data.encode()).decode()

def get_calendar_events(day, customer_id):
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'E:\Project\flask-sql-example-main\src\views\secret\client_secret.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        customer_record = db.session.query(GoogleCalendar).filter_by(id=customer_id).first()
        encrypted_calendar_id = customer_record.calendar_id
        encryption_key = customer_record.key
        calendar_id = decrypt_data(encrypted_calendar_id, encryption_key)

        now = dt.datetime.now(dt.timezone.utc).isoformat()
        future_date = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=day)).isoformat()

        events_result = service.events().list(
            calendarId=calendar_id, timeMin=now, timeMax=future_date,
            maxResults=10, singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return {'message': 'No upcoming events found.'}

        events_list = format_data(events)
        flex_message = format_room_flex(events_list)
        response_payload = botnoipayload(flex_message)

        return response_payload

    except HttpError as error:
        return {'error': f'An error occurred: {error}'}

@bp.route('/reminder_selection', methods=['GET'])
def reminder_selection():
    bubble = create_reminder_selection_bubble()
    carousel = {
        "type": "carousel",
        "contents": [bubble]
    }
    response_payload = botnoipayload(carousel)
    return jsonify(response_payload)

@bp.route('/reminder_selection/1_day', methods=['POST'])
def reminder_1_day():
    data = request.data
    customer_id = json.loads(data)
    customer_id = customer_id['id']
    events_payload = get_calendar_events(1, customer_id)
    return jsonify(events_payload)

@bp.route('/reminder_selection/2_days', methods=['POST'])
def reminder_2_days():
    data = request.data
    customer_id = json.loads(data)
    customer_id = customer_id['id']
    events_payload = get_calendar_events(2, customer_id)
    return jsonify(events_payload)

@bp.route('/reminder_selection/3_days', methods=['POST'])
def reminder_3_days():
    data = request.data
    customer_id = json.loads(data)
    customer_id = customer_id['id']
    events_payload = get_calendar_events(3, customer_id)
    return jsonify(events_payload)

@bp.route('/reminder_selection/7_days', methods=['POST'])
def reminder_7_days():
    data = request.data
    customer_id = json.loads(data)
    customer_id = customer_id['id'] 
    events_payload = get_calendar_events(7, customer_id)
    return jsonify(events_payload)

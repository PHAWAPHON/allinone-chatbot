from datetime import datetime, timedelta
import os
import requests
import schedule
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import json
import pytz
from cryptography.fernet import Fernet
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.models import db, GoogleCalendar
from src import create_app  

LINE_ACCESS_TOKEN = "tXHRYYJuC+bAf78Ku5eR0MTdxtMXQKtAMSnParOxZU+UMKJVxElp46NtvYRwtQn4v+uMRV7QySHn02gFSP0LZKre1S/Lltc3j/mZulet+8Bio7C8Dg+5HpolBZ8uhc8r9vXLQITb30i6mQZgrswodwdB04t89/1O/w1cDnyilFU="
LINE_API_URL = "https://api.line.me/v2/bot/message/push"

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
}

app = create_app()  

def decrypt_data(data, key):
    cipher = Fernet(key)
    return cipher.decrypt(data.encode()).decode()

def get_calendar_events(day, customer_id):
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
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
        with app.app_context(): 
            service = build("calendar", "v3", credentials=creds)
            
            customer_record = db.session.query(GoogleCalendar).filter_by(id=customer_id).first()
            encrypted_calendar_id = customer_record.calendar_id
            encryption_key = customer_record.key

            calendar_id = decrypt_data(encrypted_calendar_id, encryption_key)
            
            if not calendar_id:
                return None

            now = datetime.now(pytz.utc).isoformat()
            future_date = (datetime.now(pytz.utc) + timedelta(days=day)).isoformat()

            events_result = service.events().list(
                calendarId=calendar_id, timeMin=now, timeMax=future_date,
                maxResults=10, singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])

            if not events:
                return [{'type': 'text', 'text': 'No upcoming events found.'}]

            events_list = []
            thai_tz = pytz.timezone('Asia/Bangkok')
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_dt = datetime.fromisoformat(start).astimezone(thai_tz)
                formatted_event = f"📅 *Event*: {event['summary']}\n🕒 *Start Time*: {start_dt.strftime('%d-%m-%Y %H:%M')}\n"
                events_list.append(formatted_event)

            events_text = "\n".join(events_list)
            return [{'type': 'text', 'text': events_text}]

    except HttpError as error:
        return [{'type': 'text', 'text': f'An error occurred: {error}'}]

def send_message():
    with app.app_context():
        customers = db.session.query(GoogleCalendar).all()  
        for customer in customers:
            if not customer.calendar_id:
                continue 
            
            events_payload = get_calendar_events(1, customer.id)
            if events_payload:
                payload = {
                    "to": customer.id,
                    "messages": events_payload
                }
                response = requests.post(LINE_API_URL, headers=headers, json=payload)
                print(f"Message sent to {customer.id}. Response Status Code:", response.status_code)


schedule.every().day.at("06:00").do(send_message)

# Schedule job to run every 5 minutes
#schedule.every(5).seconds.do(send_message)
try:
    while True:
        schedule.run_pending()
        print(datetime.now())
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping the scheduler.")

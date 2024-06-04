from typing import List
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from . import db

class File(db.Model):
    __tablename__ = "files"

    id = Column(String(255), primary_key=True)
    GDRIVE_FOLDER_ID = Column(String(255), nullable=True)
    GDRIVE_FOLDER_IMAGE_ID = Column(String(255), nullable=True)
    GDRIVE_FOLDER_VIDEO_ID = Column(String(255), nullable=True)
    GDRIVE_FOLDER_AUDIO_ID = Column(String(255), nullable=True)

class GoogleCalendar(db.Model):
    __tablename__ = "google_calendars"

    id = Column(String(255), primary_key=True)
    calendar_id  = Column(String, nullable=True)
    key  = Column(String, nullable=True)

class GoogleForm(db.Model):
    __tablename__ = "google_forms"

    id = Column(String(255), primary_key=True)
    form_id  = Column(String(255), nullable=True)
    edit_form_link  = Column(String(255), nullable=True)

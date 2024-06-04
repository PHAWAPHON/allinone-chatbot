from flask import Blueprint, render_template, jsonify, request, redirect
import os
import queue
import threading
from flask import Blueprint, jsonify, request, json, copy_current_request_context
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from ..models import db, File
from werkzeug.utils import secure_filename
bp = Blueprint("index", __name__, url_prefix="/")


@bp.route('/', methods=['GET'])
def index():
    customer_id = request.args.get('customer_id')
    print(customer_id)
    if not customer_id or 'id' not in customer_id:
        return render_template('index.html.jinja', customer_id=customer_id)

    customer_id = customer_id['id']
    customer = File.query.filter_by(id=customer_id).first()
    if customer:
        return render_template('index.html.jinja', customer_id=customer_id)
    else:
        customer = File(id=customer_id)
        db.session.add(customer)
        db.session.commit()
        return render_template('index.html.jinja', customer_id=customer_id)

    

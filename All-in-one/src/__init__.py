from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from .config import Config


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
cors = CORS()
limiter = Limiter(get_remote_address)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init extension
    db.init_app(app)
    cors.init_app(app)
    limiter.init_app(app)

    # Create db table
    from . import models as _
    with app.app_context():
        db.create_all()
   

    from .views import index, files,calendar_view,customer, forms, folder_contents
    app.register_blueprint(index.bp)
    app.register_blueprint(files.bp)
    app.register_blueprint(calendar_view.bp)
    app.register_blueprint(customer.bp)
    app.register_blueprint(forms.bp)
    app.register_blueprint(folder_contents.bp)
    from .exceptions import (InvalidSubjectID, MissingRequiredKey,
                             exception_handler)
    app.register_error_handler(MissingRequiredKey, exception_handler)
    app.register_error_handler(InvalidSubjectID, exception_handler)

    print("All registered routes.")
    for route in app.url_map.iter_rules():
        print(f"{route.methods} {route}")

    return app

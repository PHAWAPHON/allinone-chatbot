class Config(object):

    # Flask
    SECRET_KEY = "84b9ebfa0b5bab16df6601da5c35b0f8ebb5d062ebdddd14bff178960dfeea30"
    APPLICATION_ROOT = "/"
    PREFERRED_URL_SCHEME = "http"

    # Flask Cors
    CORS_RESOURCES = {r"/*": {"origins": "*"}}
    CORS_SUPPORTS_CREDENTIALS = True

    # Flask Limiter
    RATELIMIT_DEFAULT = "500 per hour"
    RATELIMIT_STORAGE_URI = "memory://"

    # Flask SQLAlchemy
    SQLALCHEMY_DATABASE_URI = "sqlite:///demo.db"

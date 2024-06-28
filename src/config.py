from src import config


class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = config("SECRET_KEY", default="This is a secret key")
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "None"
    SQLALCHEMY_DATABASE_URI = config("DATABASE_URL")
    SECURITY_PASSWORD_SALT = config("SECURITY_PASSWORD_SALT")

    # Mail Settings
    MAIL_DEFAULT_SENDER = config("MAIL_DEFAULT_SENDER")
    MAIL_SERVER = config("MAIL_SERVER")
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEBUG = False
    MAIL_USERNAME = config("EMAIL_USER")
    MAIL_PASSWORD = config("EMAIL_PASSWORD")

    # JWT Settings
    ACCESS_TOKEN_EXPIRY_IN_SECONDS = config("ACCESS_TOKEN_EXPIRY_IN_SECONDS")
    REFRESH_TOKEN_EXPIRY_IN_DAYS = config("REFRESH_TOKEN_EXPIRY_IN_DAYS")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

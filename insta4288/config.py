"""Insta4288 development configuration."""

import pathlib

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = b'k\xa2\x1d\xa3\x7fs\xc9\xa3\xc6\
    xb3\x96|\xc1\x89S\xe9q\xc7"|\x0f\x9c\xb0\xa6'
SESSION_COOKIE_NAME = 'login'

# File Upload to var/uploads/
INSTA4288_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = INSTA4288_ROOT/'var'/'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is var/insta4288.sqlite3
DATABASE_FILENAME = INSTA4288_ROOT/'var'/'insta4288.sqlite3'

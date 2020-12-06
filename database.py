import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os

class Database():
    def __init__(self):
        creds_location = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

        cred = credentials.Certificate(creds_location)

        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://otter-keg.firebaseio.com/'
        })


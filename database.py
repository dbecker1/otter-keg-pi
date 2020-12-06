import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os

class Database():
    drinkers = []
    def __init__(self):
        creds_location = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

        cred = credentials.Certificate(creds_location)

        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://otter-keg.firebaseio.com/'
        })
        self._init_drinkers_callback()

    def _init_drinkers_callback(self):
        db.reference("drinkers").listen(self.drinkers_callback)

    def drinkers_callback(self, value):
        drinkers = []
        for drinkerId in value.data:
            drinker = value.data[drinkerId]
            drinker["id"] = drinkerId
            drinkers.append(drinker)
        self.drinkers = drinkers

        print(self.get_active_drinker())

    def get_active_drinker(self):
        active_drinkers = [drinker for drinker in self.drinkers if drinker["isActive"]]
        if len(active_drinkers) == 0:
            return None
        return active_drinkers[0]
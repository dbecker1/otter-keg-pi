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
        print(value.data)
        if value.event_type == "patch" or type(value.data) == type(False) or list(value.data.keys())[0] == "isActive":
            data = db.reference("drinkers").get();
            self.process_drinkers(data)
        else:
            self.process_drinkers(value.data)
        print("Drinkers Updated")

    def process_drinkers(self, data):
        drinkers = []
        for drinkerId in data:
            drinker = data[drinkerId]
            drinker["id"] = drinkerId
            drinkers.append(drinker)
        drinkers.sort(key=lambda x: x["name"])
        self.drinkers = drinkers

    def get_active_drinker(self):
        active_drinkers = [drinker for drinker in self.drinkers if drinker["isActive"]]
        if len(active_drinkers) == 0:
            return None
        return active_drinkers[0]

    def activate_next_drinker(self):
        if len(self.drinkers) == 0:
            return
        for index, drinker in enumerate(self.drinkers):
            if (drinker["isActive"]):
                next_index = index + 1
                if next_index >= len(self.drinkers):
                    next_index = 0
                next_drinker = self.drinkers[next_index]
                db.reference("drinkers/" + drinker["id"]).update({"isActive": False})
                db.reference("drinkers/" + next_drinker["id"]).update({"isActive": True})

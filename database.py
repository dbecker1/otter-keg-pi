import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os

class Database():
    drinkers = []
    kegs = []
    config = {}

    def __init__(self):
        creds_location = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

        cred = credentials.Certificate(creds_location)

        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://otter-keg.firebaseio.com/'
        })
        self._init_drinkers_callback()
        self._init_kegs_callback()
        self.config = db.reference("config").get()

    def _init_drinkers_callback(self):
        db.reference("drinkers").listen(self.load_drinkers)

    def load_drinkers(self, value):
        data = db.reference("drinkers").get()
        drinkers = []
        for drinkerId in data:
            drinker = data[drinkerId]
            drinker["id"] = drinkerId
            drinkers.append(drinker)
        drinkers.sort(key=lambda x: x["name"])
        self.drinkers = drinkers
        print("Drinkers Updated")

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

    def _init_kegs_callback(self):
        db.reference("kegs").listen(self.load_kegs)

    def load_kegs(self, value):
        data = db.reference("kegs").order_by_child("isActive").equal_to(True).get()
        kegs = []
        for kegId in data:
            keg = data[kegId]
            keg["id"] = kegId
            kegs.append(keg)
        self.kegs = kegs
        print("Kegs Updated")

    def create_pour(self, pour):
        ref = db.reference("pours").push()
        ref.set(pour)
        key = ref.key
        print("Creating new pour with key ", key)
        print(pour)
        return ref.key
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os
import datetime

class Database():
    drinkers = []
    kegs = []
    config = {}
    logger = None

    def __init__(self, logger):
        self.logger = logger
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
        self.logger.debug("Drinkers Updated: {}".format(drinkers))

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
        self.logger.debug("Kegs Updated: {}".format(kegs))

    def create_pour(self, pour):
        ref = db.reference("pours").push()
        ref.set(pour)
        return ref.key

    def update_pour(self, pour_id, new_value):
        db.reference("pours/" + pour_id).update({
            "amount": new_value,
            "lastUpdate": str(datetime.datetime.now().isoformat())
        })

    def finish_pour(self, pour_id):
        db.reference("pours/" + pour_id).update({"isCurrent": False})

    def delete_pour(self, pour_id):
        db.reference("pours/" + pour_id).remove()
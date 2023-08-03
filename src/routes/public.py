import time
import traceback
import threading

from fastapi import APIRouter

from utils import save_traceback
from database_handler import DataBase

class PublicRoutes:
    def __init__(self, router: APIRouter, db):
        self.router = router
        self.db = db
        self.total_data = {}
        threading.Thread(target=self.maintain_total, daemon=True).start()
        self.router.add_api_route("/public/total", self.total, methods=["GET"])
        self.router.add_api_route("/public/locs", self.locs, methods=["GET"])

    def maintain_total(self):
        maintainer_db_conn = DataBase()
        while True:
            try:
                self.total_data = maintainer_db_conn.get_total_data()
            except Exception:
                save_traceback("/total", traceback.format_exc())
            time.sleep(60*60*24)

    def total(self):
        return self.total_data

    def locs(self):
        return self.db.get_zips()

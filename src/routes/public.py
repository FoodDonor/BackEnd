import threading
import time
import traceback
from typing import Annotated

from fastapi import APIRouter, Header

from database_handler import DataBase
from utils import save_traceback


class PublicRoutes:
    def __init__(self, router: APIRouter, db):
        self.router = router
        self.db = db
        self.total_data = {}
        threading.Thread(target=self.maintain_stats, daemon=True).start()
        self.router.add_api_route("/public/stats", self.total, methods=["GET"])
        self.router.add_api_route("/public/locs", self.locs, methods=["GET"])
        self.router.add_api_route("/public/specific", self.specific, methods=["GET"])

    def maintain_stats(self):
        maintainer_db_conn = DataBase()
        while True:
            try:
                self.total_data = maintainer_db_conn.get_total_stats()
            except Exception:
                save_traceback("/total", traceback.format_exc())
            time.sleep(60 * 60 * 24)

    def total(self):
        return self.total_data

    def locs(self):
        return {"locs": self.db.get_zips()}

    def specific(self, zip: Annotated[int, Header()]):
        return self.db.specific_locs(zip)

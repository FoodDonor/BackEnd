import datetime
import threading
import time
import traceback
from base64 import b64decode
from typing import Annotated

import orjson
from fastapi import APIRouter, Header, Response

from objects import DayDataObj
from utils import save_traceback


class DistributorRoutes:
    def __init__(self, router: APIRouter, db):
        self.router = router
        self.db = db
        self.router.add_api_route("/distributor/update_daily", self.update_day_data, methods=["POST"])
        self.router.add_api_route("/distributor/request_help", self.request_help, methods=["POST"])
        threading.Thread(target=self.remove_old_help, daemon=True).start()

    def remove_old_help(self):
        while True:
            time.sleep(60 * 10)
            try:
                self.db.remove_old_help()
            except:
                save_traceback("/distributor/remove_old_help_loop", traceback.format_exc())

    def request_help(self, response: Response, authorization: Annotated[str, Header()], loc_id: Annotated[int, Header()]):
        try:
            return self._request_help(response, authorization, loc_id)
        except:
            save_traceback("/distributor/request_help", traceback.format_exc())
            response.status_code = 500
            return {"status": "error", "message": "Internal server error. Please retry later."}

    def _request_help(self, response: Response, authorization: Annotated[str, Header()], loc_id: Annotated[int, Header()]):
        user = self.db.get_distributor_by_token(authorization)
        if not user:
            response.status_code = 401
            return {"status": "error", "message": "Invalid token"}

        if user[10] == 1:
            response.status_code = 400
            return {"status": "error", "message": "Already requested help"}

        self.db.request_help(loc_id)
        response.status_code = 200
        return {"status": "success", "message": "Help requested successfully"}

    def update_day_data(
        self, response: Response, authorization: Annotated[str, Header()], loc_id: Annotated[int, Header()], data: DayDataObj
    ):
        try:
            return self._update_day_data(response, authorization, loc_id, data)
        except:
            save_traceback("/distributor/update_daily", traceback.format_exc())
            response.status_code = 500
            return {"status": "error", "message": "Internal server error. Please retry later."}

    def _update_day_data(
        self, response: Response, authorization: Annotated[str, Header()], loc_id: Annotated[int, Header()], data: DayDataObj
    ):
        try:
            if isinstance(data.encrypted, bytes):
                data.encrypted = data.encrypted.decode()
            decoded_data = orjson.loads(b64decode(data.encrypted).decode())
        except:
            response.status_code = 412
            return {"status": "error", "message": "Encryption invalid"}

        if list(decoded_data.keys()) != ["date", "num_fed", "kgs_fed", "kgs_wasted", "manpower"]:
            response.status_code = 412
            return {"status": "error", "message": "Invalid data"}

        user = self.db.get_distributor_by_token(authorization)
        if not user or not user[0]:
            response.status_code = 401
            return {"status": "error", "message": "Invalid token"}
        user = user[0]

        try:
            datetime.datetime.strptime(decoded_data["date"], "%m-%d-%Y")
        except:
            response.status_code = 412
            return {"status": "error", "message": "Invalid date"}

        if decoded_data["manpower"] not in (0, 1, 2):
            response.status_code = 412
            return {"status": "error", "message": "Invalid manpower value"}

        if decoded_data["num_fed"] < 0 or decoded_data["kgs_fed"] < 0 or decoded_data["kgs_wasted"] < 0:
            response.status_code = 412
            return {"status": "error", "message": "Invalid data"}

        self.db.insert_daily_data(
            decoded_data["date"],
            loc_id,
            decoded_data["num_fed"],
            decoded_data["kgs_fed"],
            decoded_data["kgs_wasted"],
            decoded_data["manpower"],
        )
        response.status_code = 200
        return {"status": "success", "message": "Data updated successfully"}

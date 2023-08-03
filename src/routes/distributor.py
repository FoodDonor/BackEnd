import traceback
from typing import Annotated
from fastapi import APIRouter, Response, Header

from objects import UpdateObj, DayDataObj
from utils import save_traceback


class DistributorRoutes:
    def __init__(self, router: APIRouter, db):
        self.router = router
        self.db = db
        self.router.add_api_route("/distributor/edit", self.edit_location, methods=["POST"])

    def edit_location(self, response: Response, authoriaztion: Annotated[str, Header()], loc_id: Annotated[int, Header()], data: UpdateObj):
        """
        Edit basic details of the location
        """
        try:
            user = self.db.get_distributor_by_token(authoriaztion)
            if not user:
                response.status_code = 401
                return {"status": "error", "message": "Invalid token"}
            user = user[0]
            ...
        except Exception:
            save_traceback("/register", traceback.format_exc())
            response.status_code = 500
            return {"status": "error", "message": "Internal server error. Please retry later."}

    def update_day_data(self, response: Response, authoriaztion: Annotated[str, Header()], loc_id: Annotated[int, Header()], data: DayDataObj):
        """
        Update daily data of the location
        """
        try:
            user = self.db.get_distributor_by_token(authoriaztion)
            if not user:
                response.status_code = 401
                return {"status": "error", "message": "Invalid token"}
            user = user[0]
            ...
        except Exception:
            save_traceback("/register", traceback.format_exc())
            response.status_code = 500
            return {"status": "error", "message": "Internal server error. Please retry later."}

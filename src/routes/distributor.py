import traceback
from typing import Annotated
from fastapi import APIRouter, Response, Header

from objects import UpdateObj
from utils import save_traceback


class DistributorRoutes:
    def __init__(self, router: APIRouter, db):
        self.router = router
        self.db = db
        self.router.add_api_route("/distributor/edit", self.update_location, methods=["POST"])

    def update_location(self, response: Response, authoriaztion: Annotated[str, Header()], data: UpdateObj):
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

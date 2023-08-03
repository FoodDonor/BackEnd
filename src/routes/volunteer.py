import traceback
from typing import Annotated
from fastapi import APIRouter, Response, Header

from utils import save_traceback


class VolunteerRoutes:
    def __init__(self, router: APIRouter, db):
        self.db = db
        self.router = router
        self.router.add_api_route("/volunteer/locs", self.volunteer_locs, methods=["GET"])

    def volunteer_locs(self, response: Response, authoriaztion: Annotated[str, Header()]):
        try:
            return self._volunteer_locs(response, authoriaztion)
        except:
            save_traceback("/register", traceback.format_exc())
            response.status_code = 500
            return {"status": "error", "message": "Internal server error. Please retry later."}

    def _volunteer_locs(self, response: Response, authoriaztion: Annotated[str, Header()], zip: Annotated[int, Header()]):
        user = self.db.get_distributor_by_token(authoriaztion)
        if not user:
            response.status_code = 401
            return {"status": "error", "message": "Invalid token"}
        user = user[0]
        return {"status": "success", "message": "Locations fetched successfully", "locations": self.db.get_locs_by_zip(zip)}

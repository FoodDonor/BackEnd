import traceback
from typing import Annotated

from fastapi import APIRouter, Header, Response

from utils import save_traceback


class VolunteerRoutes:
    def __init__(self, router: APIRouter, db):
        self.db = db
        self.router = router
        self.router.add_api_route("/volunteer/locs", self.volunteer_locs, methods=["GET"])

    def volunteer_locs(self, response: Response, authorization: Annotated[str, Header()], zip: Annotated[int, Header()]):
        try:
            return self._volunteer_locs(response, authorization, zip)
        except:
            save_traceback("/register", traceback.format_exc())
            response.status_code = 500
            return {"status": "error", "message": "Internal server error. Please retry later."}

    def _volunteer_locs(self, response: Response, authorization: Annotated[str, Header()], zip: Annotated[int, Header()]):
        vol = self.db.get_volunteer_by_token(authorization)
        dist = self.db.get_distributor_by_token(authorization)
        if not vol:
            if not dist:
                response.status_code = 401
                return {"status": "error", "message": "Invalid token"}

        response.status_code = 200
        return {"status": "success", "message": "Locations fetched successfully", "locations": self.db.get_locs_by_zip(zip)}

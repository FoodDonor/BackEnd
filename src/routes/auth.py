import time
import traceback
from base64 import b64decode
from uuid import uuid4
import datetime
import orjson
from fastapi import APIRouter, Response

from database_handler import DataBase
from objects import User
from utils import ceaser, hash_password, save_traceback

class ValidationError(BaseException):
    pass

class AuthRoutes:
    def __init__(self, router: APIRouter, db: DataBase):
        self.router = router
        self.db = db
        self.router.add_api_route("/auth/register", self.register, methods=["POST"])
        self.router.add_api_route("/auth/login", self.login, methods=["POST"])

    def register(self, response: Response, user: User):
        try:
            try:
                if isinstance(user.encrypted, bytes):
                    user.encrypted = user.encrypted.decode()
                decoded_user = orjson.loads(b64decode(user.encrypted).decode())
            except:
                response.status_code = 412
                return {"status": "error", "message": "Encryption invalid"}

            if self.db.check_distributor_email_exists(decoded_user["email"]) or self.db.check_volunteer_email_exists(decoded_user["phone"]):
                response.status_code = 409
                return {"status": "error", "message": "Email already exists"}
            if self.db.check_distributor_phone_exists(decoded_user["phone"]) or self.db.check_volunteer_phone_exists(decoded_user["phone"]):
                response.status_code = 409
                return {"status": "error", "message": "Phone already exists"}

            decoded_user["token"] = str(uuid4())
            decoded_user["time"] = int(time.time())
            decoded_user["password"] = hash_password(decoded_user["password"])

            # variable validation
            if decoded_user["access"].startswith("+"):
                try:
                    int(decoded_user["access"][1:])
                except:
                    raise ValidationError("Phone number is invalid.")
            else:
                if "@" not in decoded_user["access"] or "." not in decoded_user["access"] or "." not in decoded_user["access"].split("@")[1]:
                    raise ValidationError("Email is invalid.")
                if len(decoded_user["access"]) < 5:
                    raise ValidationError("Email is invalid.")
            if len(set(decoded_user["password"])) < 4:
                raise ValidationError("Password is too weak.")
            if 8 > len(decoded_user["password"]) > 32:
                raise ValidationError("Password length is invalid.")

            if " " not in decoded_user["name"]:
                raise ValidationError("Name is invalid.")
            if len(decoded_user["name"].split(" ")[0]) < 2 or len(decoded_user["name"].split(" ")[1]) < 2:
                raise ValidationError("Name is invalid.")
            if len(decoded_user["name"]) > 88:
                raise ValidationError("Name is invalid.")

            try:
                dob = datetime.datetime.strptime(decoded_user["dob"], "%m-%d-%Y").timestamp()
            except:
                raise ValidationError("Date of birth is invalid.")

            if int(datetime.now().timestamp()) - dob / 60 * 60 * 24 * 365.25 < 18:
                raise ValidationError("You must be 18 years or older to register.")
            if int(datetime.now().timestamp()) - dob / 60 * 60 * 24 * 365.25 > 123:
                raise ValidationError("Date of birth is invalid.")

            loc_id = self.db.new_user(user)

            response.status_code = 200
            response.set_cookie(key="authorization", value=decoded_user["token"])

            if loc_id != " ":
                response.set_cookie(key="location_id", value=loc_id)
                return {"status": "success", "message": "User registered successfully", "location_id": loc_id, "authorization": decoded_user["token"]}
            return {"status": "success", "message": "User registered successfully", "authorization": decoded_user["token"]}
        except ValidationError:
            response.status_code = 412
            return {"status": "error", "message": str(ValidationError)}
        except Exception:
            save_traceback("/register", traceback.format_exc())
            response.status_code = 500
            return {"status": "error", "message": "Internal server error. Please retry later."}

    def login(self, response: Response, user: User):
        try:
            if isinstance(user.encrypted, bytes):
                user.encrypted = user.encrypted.decode()
            decoded_user = orjson.loads(b64decode(ceaser(b64decode(user.encrypted).decode())))
        except:
            response.status_code = 412
            return {"status": "error", "message": "Encryption invalid"}

        if decoded_user["access"].startswith("+"):
            user = self.db.get_user_by_phone(decoded_user["access"])
        else:
            user = self.db.get_user_by_email(decoded_user["access"])

        if not user:
            response.status_code = 404
            return {"status": "error", "message": "Phone number is not registered."}
        if user["password"] != hash_password(decoded_user["password"]):
            response.status_code = 403
            return {"status": "error", "message": "Password is incorrect."}

        response.status_code = 200
        response.set_cookie(key="authorization", value=user["token"])

        if "location_id" in user:
            response.set_cookie(key="location_id", value=user["location_id"])
            return {"status": "success", "message": "User logged in successfully.", "location_id": user["location_id"], "authorization": user["token"]}
        return {"status": "success", "message": "User logged in successfully.", "authorization": user["token"]}

import time
import traceback
from base64 import b64decode
from uuid import uuid4

import orjson
from fastapi import APIRouter, Request, Response

from database_handler import DataBase
from objects import User
from utils import ceaser, hash_password, save_traceback

router = APIRouter()
db = DataBase()


@router.post("/register")
def register(request: Request, response: Response, user: User):
    try:
        if db.check_lister_email_exists(user.email) or db.check_volunteer_email_exists(user.phone):
            response.status_code = 409
            return {"status": "error", "message": "Email already exists"}
        if db.check_lister_phone_exists(user.phone) or db.check_volunteer_phone_exists(user.phone):
            response.status_code = 409
            return {"status": "error", "message": "Phone already exists"}

        try:
            if isinstance(user.encrypted, bytes):
                user.encrypted = user.encrypted.decode()
            decoded_user = orjson.loads(b64decode(ceaser(b64decode(user.encrypted).decode())))
        except:
            response.status_code = 412
            return {"status": "error", "message": "Encryption invalid"}

        decoded_user["token"] = str(uuid4())
        decoded_user["time"] = int(time.time())
        decoded_user["password"] = hash_password(decoded_user["password"])

        db.new_user(user)
        response.status_code = 200
        response.set_cookie(key="authorization", value=decoded_user["token"])
        return {"status": "success", "message": "User registered successfully"}
    except Exception:
        save_traceback("/register", traceback.format_exc())
        response.status_code = 500
        return {"status": "error", "message": "Internal server error. Please retry later."}

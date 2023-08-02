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
        try:
            if isinstance(user.encrypted, bytes):
                user.encrypted = user.encrypted.decode()
            decoded_user = orjson.loads(b64decode(ceaser(b64decode(user.encrypted).decode())))
        except:
            response.status_code = 412
            return {"status": "error", "message": "Encryption invalid"}

        if db.check_distributor_email_exists(decoded_user["email"]) or db.check_volunteer_email_exists(decoded_user["phone"]):
            response.status_code = 409
            return {"status": "error", "message": "Email already exists"}
        if db.check_distributor_phone_exists(decoded_user["phone"]) or db.check_volunteer_phone_exists(decoded_user["phone"]):
            response.status_code = 409
            return {"status": "error", "message": "Phone already exists"}

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

@router.post("/login")
def login(request: Request, response: Response, user: User):
    try:
        if isinstance(user.encrypted, bytes):
            user.encrypted = user.encrypted.decode()
        decoded_user = orjson.loads(b64decode(ceaser(b64decode(user.encrypted).decode())))
    except:
        response.status_code = 412
        return {"status": "error", "message": "Encryption invalid"}

    if decoded_user["access"].startswith("+"):
        user = db.get_user_by_phone(decoded_user["access"])
    else:
        user = db.get_user_by_email(decoded_user["access"])

    if not user:
        response.status_code = 404
        return {"status": "error", "message": "Phone number is not registered."}
    if user["password"] != hash_password(decoded_user["password"]):
        response.status_code = 403
        return {"status": "error", "message": "Password is incorrect."}

    response.status_code = 200
    response.set_cookie(key="authorization", value=user["token"])
    return {"status": "success", "message": "User logged in successfully."}

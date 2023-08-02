import time
import traceback
from base64 import b64decode
from uuid import uuid4

import orjson
import uvicorn
from fastapi import FastAPI, Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import Response

from config_handler import ConfigHandler
from database_handler import DataBase
from objects import User
from utils import hash_password, ceaser

config = ConfigHandler(fn="config.json")
db = DataBase()
app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def save_traceback(source, tb, message="none"):
    with open("traceback.log", "a") as f:
        f.write(
            f"""============================
At {source} on {int(time.time())} with message {message}
============================
{tb}
============================\n
"""
        )



@app.post("/register")
@limiter.limit("3/10second")
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


uvicorn.run(app, host="127.0.0.1", port=config.get("host_port"))

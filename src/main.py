import uvicorn
from fastapi import FastAPI

from config_handler import ConfigHandler
from database_handler import DataBase
from routes import auth

config = ConfigHandler(fn="config.json")
db = DataBase()
app = FastAPI()
app.include_router(auth.router)

uvicorn.run(app, host="127.0.0.1", port=config.get("host_port"))

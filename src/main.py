import orjson
import uvicorn
from fastapi import FastAPI

from database_handler import DataBase
from routes import auth, distributor, public, volunteer

db = DataBase()
app = FastAPI()
router = app.router
port = orjson.loads(open("config.json").read())["host_port"]

distributor.DistributorRoutes(router, db)
volunteer.VolunteerRoutes(router, db)
public.PublicRoutes(router, db)
auth.AuthRoutes(router, db)

uvicorn.run(app, host="127.0.0.1", port=port)

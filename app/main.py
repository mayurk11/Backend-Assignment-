from fastapi import FastAPI
from app.database import engine, Base
from app.routers import router
import app.models


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)

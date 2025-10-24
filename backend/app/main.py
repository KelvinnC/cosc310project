from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.routers.movies import router as movies_router
from app.routers.user_endpoints import router as users_router
from app.routers.login import router as login_router

app = FastAPI()

@app.get("/")
def root():
        return {"message": "Hello Movie World!"}

app.include_router(movies_router)
app.include_router(users_router)
app.include_router(login_router)
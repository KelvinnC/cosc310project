from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.routers.movies import router as movies_router
from app.routers.user_endpoints import router as users_router
from app.routers.battles import router as battles_router
from app.routers.reviews import router as reviews_router
from app.routers.admin_endpoints import router as admin_router
try:
    from app.routers.login import router as login_router
except Exception:
    login_router = None

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello Movie World!"}

app.include_router(movies_router)
app.include_router(users_router)
app.include_router(reviews_router)
app.include_router(admin_router)
if login_router is not None:
    app.include_router(login_router)
app.include_router(battles_router)



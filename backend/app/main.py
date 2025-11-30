from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
from app.routers.movies import router as movies_router
from app.routers.user_endpoints import router as users_router
from app.routers.battles import router as battles_router
from app.routers.reviews import router as reviews_router
from app.routers.admin_endpoints import router as admin_router
from app.routers.user_home import router as home_router
from app.routers.leaderboard import router as leaderboard_router
try:
    from app.routers.login import router as login_router
except Exception:
    login_router = None

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

@app.get("/")
def root():
    return {"message": "Hello Movie World!"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(movies_router)
app.include_router(users_router)
app.include_router(reviews_router)
app.include_router(admin_router)
if login_router is not None:
    app.include_router(login_router)
app.include_router(battles_router)
app.include_router(home_router)
app.include_router(leaderboard_router)
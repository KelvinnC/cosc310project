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
from app.routers.achievements import router as achievements_router
from app.routers.login import router as login_router
from app.routers.tmdb import router as tmdb_router
from app.routers.watchlist_endpoints import router as watchlist_router

app = FastAPI(
    title="Review Battle API",
    description="A movie review platform with head-to-head review battles, leaderboards, and achievements.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]


@app.get("/", tags=["status"], summary="API Health Check")
def root():
    """
    Root endpoint providing API status and navigation links.

    Use this to verify the API is running and discover available endpoints.
    """
    return {
        "name": "Review Battle API",
        "version": "1.0.0",
        "status": "healthy",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "movies": "/movies",
            "reviews": "/reviews",
            "users": "/users",
            "battles": "/battles",
            "leaderboard": "/leaderboard",
            "achievements": "/achievements",
            "admin": "/admin",
            "tmdb": "/tmdb"
        }
    }


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
app.include_router(login_router)
app.include_router(battles_router)
app.include_router(home_router)
app.include_router(leaderboard_router)
app.include_router(tmdb_router)
app.include_router(watchlist_router)
app.include_router(achievements_router)

from fastapi import FastAPI
from app.routers.movies import router as movies_router
from app.routers.users import router as users_router
from app.routers.searches import router as searches_router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello Movie World!"}

app.include_router(movies_router)
app.include_router(users_router)
app.include_router(searches_router)

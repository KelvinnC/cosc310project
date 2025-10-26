from fastapi import FastAPI
from app.routers.movies import router as movies_router
from app.routers.users import router as users_router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello Movie World!"}

# Include routers
app.include_router(movies_router)
app.include_router(users_router)

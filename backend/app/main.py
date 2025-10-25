from fastapi import FastAPI
from app.routers.movies import router as movies_router

app = FastAPI()

@app.get("/")
def root():
        return {"message": "Hello Movie World!"}

app.include_router(movies_router)

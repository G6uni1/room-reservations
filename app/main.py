from fastapi import FastAPI
from app.routers import auth, resources
from app.routers import auth, resources, reservations

app = FastAPI(title="Room Reservations API")

app.include_router(auth.router)
app.include_router(resources.router)
app.include_router(reservations.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
from fastapi import FastAPI

app = FastAPI(title="Room Reservations API")

@app.get("/health")
def health_check():
    return {"status": "ok"}
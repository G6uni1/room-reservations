from fastapi import FastAPI

app = FastAPI(title="Sistema de Reservas de Salas")

@app.get("/health")
def health_check():
    return {"status": "ok"}
from fastapi import FastAPI

app = FastAPI()

@app.get("/admin-stats")
def get_stats():
    return {
        "service": "internal-user-service",
        "data": "Sensible Backend-Informationen erfolgreich über Gateway empfangen."
    }

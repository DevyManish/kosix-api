import uvicorn
from fastapi import FastAPI
from app.core.config import settings

app = FastAPI()

@app.get("/")
def home():
    return {"status": "online", "port": settings.PORT}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True
    )

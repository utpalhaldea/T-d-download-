import os

from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="TeraBox / Diskwala Downloader",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "TeraBox / Diskwala Downloader",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )

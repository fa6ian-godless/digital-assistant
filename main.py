from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from routers.meeting_router import router as meeting_router
from routers.record_router import router as record_router
from config import UPLOAD_DIR
from config import TRANSCRIPT_DIR
from config import RESULTS_DIR

app = FastAPI(
    title = "Digital Assistant",
    description = "Цифровой ассистент совещаний"
)

app.mount("/static", StaticFiles(directory = "static"), name = "static")

app.include_router(meeting_router)
app.include_router(record_router)


@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host = "127.0.0.0", port = 8000)
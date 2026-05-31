import shutil
from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from pathlib import Path

from schemas.transcription import TranscriptionResponse
from services.whisper_service import WhisperService
from config import UPLOAD_DIR

router = APIRouter(prefix = "/api", tags = ["record"])


@router.post("/upload-record")
async def upload_record(file: UploadFile = File(...)):
    
    if not file.filename.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.mp4', '.webm')):
        raise HTTPException(400, detail = "Поддерживаются аудио/видео файлы")

    file_path = UPLOAD_DIR / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return JSONResponse({
        "status": "uploaded",
        "filename": file.filename,
        "path": str(file_path),
        "message": "Файл загружен."
    })


@router.post("/transcribe", response_model = TranscriptionResponse)
async def transcribe_record(filename: str):
    
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(404, detail = "Файл не найден.")

    result = await WhisperService.transcribe_record(str(file_path))
    
    return result
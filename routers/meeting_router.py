import json
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

from schemas.meeting import MeetingProcessingResult
from services.ollama_service import OllamaService
from config import TRANSCRIPT_DIR
from config import RESULTS_DIR

router = APIRouter(prefix = "/api", tags = ["meeting"])


@router.post("/process-meeting")
async def process_meeting(transcript_filename: str):
    
    transcript_path = TRANSCRIPT_DIR / transcript_filename
    
    if not transcript_path.exists():
        raise HTTPException(404, detail = "Транскрипт не найден")

    with open(transcript_path, "r", encoding = "utf-8") as file:
        transcript = json.load(file)

    full_text = transcript["full_text"]

    speakers = await OllamaService.label_speakers(transcript)

    tasks = await OllamaService.extract_tasks(full_text, speakers)

    protocol_md = await OllamaService.generate_protocol(full_text, speakers, tasks)

    result = {
        "filename": transcript["filename"],
        "full_text": full_text,
        "speakers": speakers,
        "tasks": tasks,
        "protocol_markdown": protocol_md,
        "transcript_file": str(transcript_path),
    }

    result_path = RESULTS_DIR / f"{Path(transcript_filename).stem}_result.json"

    with open(result_path, "w", encoding = "utf-8") as file:
        json.dump(result, file, ensure_ascii = False, indent = 2)

    return MeetingProcessingResult(**result, result_file = str(result_path))
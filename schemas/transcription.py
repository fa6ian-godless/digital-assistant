from pydantic import BaseModel
from typing import List
from typing import Optional

class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str

class TranscriptionResponse(BaseModel):
    status: str
    message: str
    language: str
    duration: float
    segments_count: int
    transcript_file: str
    full_text_preview: str
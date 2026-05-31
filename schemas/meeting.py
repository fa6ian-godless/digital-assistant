from pydantic import BaseModel
from typing import List, Dict, Optional

class SpeakerMapping(BaseModel):
    speaker_id: str
    name: str
    role: Optional[str]

class Task(BaseModel):
    description: str
    assignee: str
    deadline: Optional[str]
    status: str = "Новая"

class MeetingProcessingResult(BaseModel):
    filename: str
    full_text: str
    speakers: List[SpeakerMapping]
    tasks: List[Task]
    protocol_markdown: str
    transcript_file: str
    result_file: str
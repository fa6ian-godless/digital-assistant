import time
import json
from pathlib import Path
from faster_whisper import WhisperModel

from config import TRANSCRIPT_DIR
from config import WHISPER_MODEL_SIZE
from config import WHISPER_DEVICE
from config import WHISPER_COMPUTE_TYPE

class WhisperService:

    _model = None

    
    @classmethod
    def get_model(cls):
        
        if cls._model is None:
            
            print(f"Загрузка модели faster-whisper: {WHISPER_MODEL_SIZE} на {WHISPER_DEVICE}...")
            
            cls._model = WhisperModel(
                WHISPER_MODEL_SIZE,
                device = WHISPER_DEVICE,
                compute_type = WHISPER_COMPUTE_TYPE
            )

            print("Модель whisper загружена!")
        
        return cls._model


    @staticmethod
    async def transcribe_record(file_path: str) -> dict:
        
        model = WhisperService.get_model()
        start_time = time.time()

        segments, info = model.transcribe(
            file_path,
            beam_size = 5,
            vad_filter = True,
            language = None
        )

        transcript_segments = []
        full_text = ""

        for segment in segments:

            transcript_segments.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip()
            })

            full_text += segment.text.strip() + " "

        processing_time = round(time.time() - start_time, 2)

        result = {
            "filename": Path(file_path).name,
            "language": info.language,
            "language_probability": round(info.language_probability, 4),
            "duration": round(info.duration, 2),
            "processing_time_seconds": processing_time,
            "segments": transcript_segments,
            "full_text": full_text.strip()
        }

        output_path = TRANSCRIPT_DIR / f"{Path(file_path).stem}_transcript.json"

        with open(output_path, "w", encoding = "utf-8") as file:
            json.dump(result, file, ensure_ascii = False, indent = 2)

        return {
            "status": "success",
            "message": f"Транскрипция завершена за {processing_time} сек.",
            "language": info.language,
            "duration": info.duration,
            "segments_count": len(transcript_segments),
            "transcript_file": str(output_path),
            "full_text_preview": full_text.strip()[:500] + "..." if len(full_text) > 500 else full_text.strip()
        }
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from enum import Enum

class GenerationStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class PipelineType(str, Enum):
    TEXT_TO_IMAGE = "text_to_image"  # Только изображение
    FULL_PIPELINE = "full_pipeline"  # Текст → Изображение → Видео
    CHARACTER = "character"  # Создание персонажа

class GenerationRequest(BaseModel):
    prompt: str
    pipeline_type: PipelineType = PipelineType.FULL_PIPELINE
    aspect_ratio: str = "1:1"
    style_preset: Optional[str] = None  # 👈 Можно использовать для motion effects

class GenerationResponse(BaseModel):
    job_id: str
    status: GenerationStatus
    message: str

class PipelineStatusResponse(BaseModel):
    pipeline_id: str
    status: GenerationStatus
    steps: List[Dict[str, Any]]
    final_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import uuid
import logging

from schemas import GenerationRequest, GenerationResponse, PipelineStatusResponse, GenerationStatus
from services.higgsfield_api import HiggsfieldAPIClient
from config import HiggsfieldModels

router = APIRouter(prefix="/api/v1", tags=["generation"])

# In-memory storage
pipeline_statuses = {}

# 👇 Инициализируем реальный клиент
client = HiggsfieldAPIClient()

@router.post("/generate", response_model=GenerationResponse)
async def start_generation(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Запуск пайплайна генерации с реальными моделями Higgsfield"""
    
    if not request.prompt:
        raise HTTPException(status_code=422, detail="Prompt is required")
    
    pipeline_id = str(uuid.uuid4())
    
    # Инициализируем статус пайплайна
    pipeline_statuses[pipeline_id] = {
        "status": GenerationStatus.PROCESSING,
        "prompt": request.prompt,
        "pipeline_type": request.pipeline_type,
        "steps": [],
        "final_result": None,
        "error": None
    }
    
    # Запускаем в фоне
    background_tasks.add_task(
        execute_real_generation_pipeline,
        pipeline_id,
        request
    )
    
    return GenerationResponse(
        job_id=pipeline_id,
        status=GenerationStatus.PROCESSING,
        message=f"Generation pipeline started for: {request.prompt}"
    )

async def execute_real_generation_pipeline(pipeline_id: str, request: GenerationRequest):
    """Выполнение пайплайна генерации с реальными моделями Higgsfield"""
    
    try:
        steps = []
        final_image_url = None
        final_video_url = None
        
        # 👇 ШАГ 1: Генерация изображения через Text to Image [Soul]
        steps.append({"step": "text_to_image", "status": "processing", "model": "Soul"})
        pipeline_statuses[pipeline_id]["steps"] = steps
        
        print("🎨 Шаг 1: Генерация изображения из текста...")
        image_result = client.generate_image(
            prompt=request.prompt,
            aspect_ratio=request.aspect_ratio
        )
        
        if not image_result:
            raise Exception("❌ Генерация изображения не удалась")
        
        image_url = client.extract_result_url(image_result)
        if not image_url:
            raise Exception("❌ Не удалось получить URL изображения")
        
        steps[-1]["status"] = "completed"
        steps[-1]["result_url"] = image_url
        final_image_url = image_url
        
        print(f"✅ Изображение создано: {image_url}")
        
        # Обновляем статус
        pipeline_statuses[pipeline_id]["steps"] = steps
        pipeline_statuses[pipeline_id]["final_result"] = {
            "image_url": final_image_url,
            "type": "image",
            "source": "Higgsfield Soul"
        }
        
        # 👇 ШАГ 2: Если нужен полный пайплайн (изображение → видео)
        if request.pipeline_type == "full_pipeline":
            steps.append({"step": "image_to_video", "status": "processing", "model": "DoP"})
            pipeline_statuses[pipeline_id]["steps"] = steps
            
            print("🎥 Шаг 2: Преобразование изображения в видео...")
            
            # Создаем промпт для видео на основе оригинального
            video_prompt = f"Dynamic video of: {request.prompt}"
            
            video_result = client.generate_video_from_image(
                image_url=image_url,
                prompt=video_prompt,
                aspect_ratio=request.aspect_ratio,
                motion_effect=request.style_preset  # 👈 Можно использовать для motion effects
            )
            
            if not video_result:
                raise Exception("❌ Генерация видео не удалась")
            
            video_url = client.extract_result_url(video_result)
            if not video_url:
                raise Exception("❌ Не удалось получить URL видео")
            
            steps[-1]["status"] = "completed"
            steps[-1]["result_url"] = video_url
            final_video_url = video_url
            
            print(f"✅ Видео создано: {video_url}")
            
            # Финальный результат
            pipeline_statuses[pipeline_id]["final_result"] = {
                "image_url": final_image_url,
                "video_url": final_video_url,
                "type": "video",
                "source": "Higgsfield DoP"
            }
        
        # 👇 ШАГ 3: Альтернатива - создание персонажа
        elif request.pipeline_type == "character":
            steps.append({"step": "create_character", "status": "processing", "model": "Soul ID"})
            pipeline_statuses[pipeline_id]["steps"] = steps
            
            print("👤 Шаг 2: Создание персонажа...")
            
            character_result = client.create_character(
                prompt=request.prompt,
                character_name="Generated Character"
            )
            
            if character_result:
                character_url = client.extract_result_url(character_result)
                if character_url:
                    steps[-1]["status"] = "completed"
                    steps[-1]["result_url"] = character_url
                    
                    pipeline_statuses[pipeline_id]["final_result"] = {
                        "character_url": character_url,
                        "image_url": final_image_url,  # Первое изображение как превью
                        "type": "character",
                        "source": "Higgsfield Soul ID"
                    }
        
        # Успешное завершение
        pipeline_statuses[pipeline_id]["status"] = GenerationStatus.COMPLETED
        print("🎉 Весь пайплайн завершен успешно!")
        
    except Exception as e:
        logging.error(f"❌ Пайплайн {pipeline_id} завершился ошибкой: {e}")
        pipeline_statuses[pipeline_id]["status"] = GenerationStatus.FAILED
        pipeline_statuses[pipeline_id]["error"] = str(e)

@router.get("/status/{pipeline_id}", response_model=PipelineStatusResponse)
async def get_pipeline_status(pipeline_id: str):
    """Получение статуса пайплайна"""
    
    if pipeline_id not in pipeline_statuses:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    status_data = pipeline_statuses[pipeline_id]
    
    return PipelineStatusResponse(
        pipeline_id=pipeline_id,
        status=status_data["status"],
        steps=status_data["steps"],
        final_result=status_data["final_result"],
        error=status_data["error"]
    )

# 👇 НОВЫЙ ЭНДПОИНТ для прямой генерации изображений
@router.post("/generate/image")
async def generate_image_only(request: Dict[str, Any]):
    """Только генерация изображения"""
    if not request.get("prompt"):
        raise HTTPException(status_code=422, detail="Prompt is required")
    
    result = client.generate_image(
        prompt=request.get("prompt"),
        aspect_ratio=request.get("aspect_ratio", "1:1")
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Image generation failed")
    
    image_url = client.extract_result_url(result)
    
    return {
        "success": True,
        "image_url": image_url,
        "type": "image",
        "model": "Soul"
    }

# 👇 НОВЫЙ ЭНДПОИНТ для прямой генерации видео из существующего изображения
@router.post("/generate/video")
async def generate_video_only(request: Dict[str, Any]):
    """Только генерация видео из изображения"""
    if not request.get("prompt") or not request.get("image_url"):
        raise HTTPException(status_code=422, detail="Prompt and image_url are required")
    
    result = client.generate_video_from_image(
        image_url=request.get("image_url"),
        prompt=request.get("prompt"),
        aspect_ratio=request.get("aspect_ratio", "1:1"),
        motion_effect=request.get("motion_effect")
    )
    
    if not result:
        raise HTTPException(status_code=500, detail="Video generation failed")
    
    video_url = client.extract_result_url(result)
    
    return {
        "success": True,
        "video_url": video_url,
        "type": "video",
        "model": "DoP"
    }
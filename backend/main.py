from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
from services.higgsfield_api import HiggsfieldAPIClient

app = FastAPI()

# CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 👈 Разрешаем все origins для тестирования
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализируем реальный клиент Higgsfield
higgsfield_client = HiggsfieldAPIClient()

# Хранилище статусов
pipeline_statuses = {}

async def real_ai_generation_pipeline(pipeline_id: str, prompt: str, pipeline_type: str):
    """РЕАЛЬНЫЙ пайплайн генерации через Higgsfield API"""
    
    try:
        print(f"🎬 Starting REAL AI pipeline for: '{prompt}'")
        
        steps = []
        final_image_url = None
        final_video_url = None
        
        # 👇 ШАГ 1: Реальная генерация изображения
        steps.append({"step": "text_to_image", "status": "processing", "model": "Soul"})
        pipeline_statuses[pipeline_id]["steps"] = steps
        
        print("🎨 Step 1: Generating image from text...")
        image_result = higgsfield_client.generate_image(prompt)
        
        if not image_result:
            raise Exception("❌ Real image generation failed")
        
        final_image_url = higgsfield_client.extract_image_url(image_result)
        if not final_image_url:
            raise Exception("❌ Could not get image URL")
        
        steps[-1]["status"] = "completed"
        steps[-1]["result_url"] = final_image_url
        
        print(f"✅ Image generated: {final_image_url}")
        
        # Обновляем промежуточный результат
        pipeline_statuses[pipeline_id]["steps"] = steps
        pipeline_statuses[pipeline_id]["final_result"] = {
            "image_url": final_image_url,
            "type": "image",
            "source": "Higgsfield Soul"
        }
        
        # 👇 ШАГ 2: Реальная генерация видео (если полный пайплайн)
        if pipeline_type == "full_pipeline":
            steps.append({"step": "image_to_video", "status": "processing", "model": "DoP"})
            pipeline_statuses[pipeline_id]["steps"] = steps
            
            print("🎥 Step 2: Generating video from image...")
            
            # Создаем промпт для видео на основе оригинального
            video_prompt = f"Dynamic video of: {prompt}"
            
            video_result = higgsfield_client.generate_video_from_image(
                image_url=final_image_url,
                prompt=video_prompt
            )
            
            if not video_result:
                raise Exception("❌ Real video generation failed")
            
            final_video_url = higgsfield_client.extract_video_url(video_result)
            if not final_video_url:
                raise Exception("❌ Could not get video URL")
            
            steps[-1]["status"] = "completed"
            steps[-1]["result_url"] = final_video_url
            
            print(f"✅ Video generated: {final_video_url}")
            
            # Финальный результат
            pipeline_statuses[pipeline_id]["final_result"] = {
                "image_url": final_image_url,
                "video_url": final_video_url,
                "type": "video", 
                "source": "Higgsfield Soul + DoP"
            }
        
        # Успешное завершение
        pipeline_statuses[pipeline_id]["status"] = "completed"
        print("🎉 Real AI pipeline completed successfully!")
        
    except Exception as e:
        print(f"❌ Real AI pipeline failed: {e}")
        pipeline_statuses[pipeline_id]["status"] = "failed"
        pipeline_statuses[pipeline_id]["error"] = str(e)

@app.post("/api/v1/generate")
async def generate_content(request: dict, background_tasks: BackgroundTasks):
    """Запуск РЕАЛЬНОЙ генерации через Higgsfield API"""
    
    if not request.get("prompt"):
        raise HTTPException(status_code=422, detail="Prompt is required")
    
    pipeline_id = str(uuid.uuid4())
    
    # Сохраняем статус
    pipeline_statuses[pipeline_id] = {
        "status": "processing",
        "prompt": request.get("prompt"),
        "pipeline_type": request.get("pipeline_type", "full_pipeline"),
        "steps": [],
        "final_result": None,
        "error": None
    }
    
    # 👇 Запускаем РЕАЛЬНУЮ генерацию в фоне
    background_tasks.add_task(
        real_ai_generation_pipeline,
        pipeline_id,
        request.get("prompt"),
        request.get("pipeline_type", "full_pipeline")
    )
    
    return {
        "job_id": pipeline_id,
        "status": "processing", 
        "message": f"Real AI generation started for: {request.get('prompt')}"
    }

@app.get("/api/v1/status/{pipeline_id}")
async def get_pipeline_status(pipeline_id: str):
    if pipeline_id not in pipeline_statuses:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline_statuses[pipeline_id]

@app.get("/")
async def root():
    return {"message": "🚀 HackNU Higgsfield Pipeline API is working!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "Backend server is running!",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/v1/test")
async def test_endpoint():
    return {
        "message": "✅ Test endpoint is working!",
        "server": "FastAPI",
        "status": "active"
    }

# 👇 ВАЖНО: ДОБАВЬТЕ ЗАПУСК СЕРВЕРА В КОНЦЕ ФАЙЛА
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 STARTING HACKNU HIGGSFIELD BACKEND SERVER")
    print("=" * 60)
    print("📡 URL: http://localhost:8000")
    print("🌐 Health: http://localhost:8000/health")
    print("🎯 Generate: http://localhost:8000/api/v1/generate")
    print("=" * 60)
    print("✅ SERVER IS STARTING...")
    print("💡 Open a NEW terminal to test the server")
    print("⏹️  Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Запускаем сервер
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

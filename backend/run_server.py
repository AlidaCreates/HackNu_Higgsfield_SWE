from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid

app = FastAPI()

# Максимально открытые CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все домены
    allow_credentials=True,
    allow_methods=["*"],   # Все HTTP методы
    allow_headers=["*"],   # Все заголовки
)

# Простое хранилище
jobs = {}

@app.get("/")
async def root():
    return {"message": "🚀 Server is WORKING!", "status": "active"}

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "message": "Backend server is running correctly",
        "version": "1.0.0"
    }

@app.post("/api/v1/generate")
async def generate(request: dict):
    print(f"🎯 Received request: {request.get('prompt')}")
    
    if not request.get("prompt"):
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    job_id = str(uuid.uuid4())
    
    # Имитируем обработку
    jobs[job_id] = {
        "status": "completed",
        "prompt": request.get("prompt"),
        "result": {
            "image_url": f"https://picsum.photos/800/600?{job_id}",
            "video_url": "https://sample-videos.com/mp4/720/SampleVideo_1280x720_1mb.mp4",
            "type": "video"
        }
    }
    
    return {
        "job_id": job_id,
        "status": "completed",
        "message": f"Demo generation done for: {request.get('prompt')}"
    }

@app.get("/api/v1/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

if __name__ == "__main__":
    print("=" * 50)
    print("🚀 STARTING HACKNU BACKEND SERVER")
    print("=" * 50)
    print("📡 URL: http://localhost:8001")
    print("🌐 Health: http://localhost:8001/health")
    print("🎯 Generate: http://localhost:8001/api/v1/generate")
    print("=" * 50)
    
    # Запускаем на порту 8001 (на случай если 8000 занят)
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
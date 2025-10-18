import requests
import time
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('.env.local')

class HiggsfieldAPIClient:
    def __init__(self):
        self.api_key = os.getenv("HIGGSFIELD_API_KEY")
        self.api_secret = os.getenv("HIGGSFIELD_API_SECRET")
        self.base_url = "https://platform.higgsfield.ai"
        self.headers = {
            "hf-api-key": self.api_key,
            "hf-secret": self.api_secret,
            "Content-Type": "application/json"
        }
        
        print("=" * 50)
        print("🚀 Higgsfield API Client Initialized")
        print(f"🔑 API Key: {self.api_key[:10]}..." if self.api_key else "❌ API Key not found")
        print(f"🔐 Secret: {self.api_secret[:10]}..." if self.api_secret else "❌ Secret not found")
        print("=" * 50)
        
        if not self.api_key or not self.api_secret:
            print("❌ ERROR: API credentials not found!")
            print("💡 Make sure HIGGSFIELD_API_KEY and HIGGSFIELD_API_SECRET are in .env.local")
    
    def _make_api_call(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Реальный вызов API Higgsfield"""
        try:
            if not self.api_key or not self.api_secret:
                print("❌ Missing API credentials")
                return None
                
            url = f"{self.base_url}/{endpoint}"
            print(f"🚀 API CALL to: {url}")
            print(f"📦 Request data: {data}")
            
            response = requests.post(url, json=data, headers=self.headers, timeout=60)
            
            print(f"📨 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API call successful")
                return result
            else:
                print(f"❌ API call failed: {response.status_code}")
                print(f"📄 Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"💥 API call error: {e}")
            return None

    def generate_image(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Генерация изображения через /v1/text2image/soul"""
        print(f"🎨 Generating image for: '{prompt}'")
        
        # 👇 ПРАВИЛЬНАЯ структура для Text to Image
        data = {
            "params": {
                "prompt": prompt,
                # Добавьте другие параметры из документации если нужно
            },
            "webhost": {
                "url": "<string>",  # ⚠️ Замените на реальное значение
                "secret": "<string>" # ⚠️ Замените на реальное значение
            }
        }
        
        # 👇 ПРАВИЛЬНЫЙ эндпоинт
        result = self._make_api_call("v1/text2image/soul", data)
        if not result:
            print("❌ Image generation failed")
            return None
        
        # Ожидаем завершения
        job_id = result.get("id")
        if job_id:
            return self._wait_for_completion(job_id)
        return result

    def generate_video_from_image(self, image_url: str, prompt: str) -> Optional[Dict[str, Any]]:
        """Генерация видео через /v1/motions"""
        print(f"🎥 Generating video from image")
        print(f"🖼️ Image URL: {image_url}")
        print(f"📝 Video prompt: '{prompt}'")
        
        # 👇 ПРАВИЛЬНАЯ структура для Image to Video
        data = {
            "params": {
                "prompt": prompt,
                "input_image": image_url,
                # Добавьте другие параметры если нужно
            }
        }
        
        # 👇 ПРАВИЛЬНЫЙ эндпоинт
        result = self._make_api_call("v1/motions", data)
        if not result:
            print("❌ Video generation failed")
            return None
        
        job_id = result.get("id")
        if job_id:
            return self._wait_for_completion(job_id)
        return result
    
    def _wait_for_completion(self, job_id: str, max_attempts: int = 40) -> Optional[Dict[str, Any]]:
        """Ожидание завершения генерации"""
        print(f"🔄 Waiting for job completion: {job_id}")
        
        for attempt in range(max_attempts):
            try:
                print(f"📊 Status check {attempt + 1}/{max_attempts}...")
                
                # 👇 Проверяем статус через правильный эндпоинт
                response = requests.get(
                    f"{self.base_url}/v1/jobs/{job_id}",  # ⚠️ Уточните эндпоинт для проверки статуса
                    headers=self.headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    job_data = response.json()
                    status = job_data.get("status", "unknown")
                    
                    print(f"📈 Job status: {status}")
                    
                    if status == "completed":
                        print("🎉 Generation completed!")
                        return job_data
                    elif status == "failed":
                        print("❌ Generation failed")
                        return None
                    
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️ Status check error: {e}")
                time.sleep(5)
        
        print("⏰ Timeout waiting for generation")
        return None
    
    def extract_image_url(self, job_data: Dict[str, Any]) -> str:
        """Извлечение URL изображения из ответа Higgsfield"""
        try:
            # ⚠️ АДАПТИРУЙТЕ ПОД РЕАЛЬНУЮ СТРУКТУРУ ОТВЕТА
            if job_data and "results" in job_data:
                results = job_data["results"]
                if results and len(results) > 0:
                    return results[0].get("url", "")
            
            print("❌ Could not extract image URL")
            return None
        except Exception as e:
            print(f"❌ Error extracting image URL: {e}")
            return None
    
    def extract_video_url(self, job_data: Dict[str, Any]) -> str:
        """Извлечение URL видео из ответа Higgsfield"""
        try:
            # ⚠️ АДАПТИРУЙТЕ ПОД РЕАЛЬНУЮ СТРУКТУРУ ОТВЕТА
            if job_data and "results" in job_data:
                results = job_data["results"]
                if results and len(results) > 0:
                    return results[0].get("video_url", results[0].get("url", ""))
            
            print("❌ Could not extract video URL")
            return None
        except Exception as e:
            print(f"❌ Error extracting video URL: {e}")
            return None

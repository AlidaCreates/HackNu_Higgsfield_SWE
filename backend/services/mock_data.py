import time
from typing import Dict, Any

class MockHiggsfieldClient:
    """Мок-клиент для тестирования без использования кредитов"""
    
    def __init__(self):
        self.mock_image_url = "https://example.com/sample-image.jpg"
        self.mock_video_url = "https://example.com/sample-video.mp4"
    
    def generate_image(self, prompt: str, aspect_ratio: str = "16:9") -> Dict[str, Any]:
        time.sleep(2)  # Имитация задержки
        return {
            "id": f"mock_img_{int(time.time())}",
            "jobs": [{
                "status": "completed",
                "results": {
                    "raw": {"url": self.mock_image_url, "type": "image"},
                    "min": {"url": self.mock_image_url, "type": "image"}
                }
            }],
            "input_params": {"prompt": prompt, "aspect_ratio": aspect_ratio}
        }
    
    def generate_video_from_image(self, image_url: str, prompt: str, aspect_ratio: str = "16:9") -> Dict[str, Any]:
        time.sleep(3)
        return {
            "id": f"mock_vid_{int(time.time())}",
            "jobs": [{
                "status": "completed",
                "results": {
                    "url": self.mock_video_url,
                    "type": "video"
                }
            }],
            "input_params": {"prompt": prompt, "input_images": [image_url]}
        }
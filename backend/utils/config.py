import os
from dotenv import load_dotenv

load_dotenv('.env.local')

HIGGSFIELD_API_KEY = os.getenv("HIGGSFIELD_API_KEY")
HIGGSFIELD_API_SECRET = os.getenv("HIGGSFIELD_API_SECRET") 
HIGGSFIELD_BASE_URL = "https://platform.higgsfield.ai/v1"

# 👇 МОДЕЛИ ИЗ ВАШЕЙ ДОКУМЕНТАЦИИ
class HiggsfieldModels:
    IMAGE_TO_VIDEO_DOP = "dop"  # Image to Video [DoP]
    TEXT_TO_IMAGE_SOUL = "soul"  # Text to Image [Soul] 
    CREATE_CHARACTER_SOUL_ID = "soul-id"  # Create character [Soul ID]

class PipelineConfig:
    MAX_RETRIES = 30
    RETRY_DELAY = 5
    TIMEOUT = 300
    
if not HIGGSFIELD_API_KEY or not HIGGSFIELD_API_SECRET:
    print("⚠️  WARNING: HIGGSFIELD_API_KEY or HIGGSFIELD_API_SECRET not found in .env.local")
    print("💡 Make sure to add your API credentials to backend/.env.local")
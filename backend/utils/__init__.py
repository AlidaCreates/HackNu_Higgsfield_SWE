import json
import logging
from typing import Any, Dict

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def extract_result_url(job_data: Dict[str, Any]) -> str:
    """Извлечение URL результата из ответа API"""
    try:
        if job_data and "jobs" in job_data and job_data["jobs"]:
            job = job_data["jobs"][0]
            if job["status"] == "completed" and job.get("results"):
                # Предпочитаем raw качество, если доступно
                if "raw" in job["results"]:
                    return job["results"]["raw"]["url"]
                elif "min" in job["results"]:
                    return job["results"]["min"]["url"]
                # Для видео может быть другой формат
                elif "url" in job["results"]:
                    return job["results"]["url"]
        return None
    except Exception as e:
        logging.error(f"Error extracting result URL: {e}")
        return None
# suno_strategy.py
import requests
from django.conf import settings
from .base_strategy import SongGeneratorStrategy
from music.models import SongGenerationRequest

class SunoSongGeneratorStrategy(SongGeneratorStrategy):
    """Strategy that interacts with the Suno API."""
    
    def generate(self, request: SongGenerationRequest) -> dict:
        url = "https://api.sunoapi.org/api/v1/generate"
        headers = {
            "Authorization": f"Bearer {settings.SUNO_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": request.parameters.prompt, 
            "style": f"{request.parameters.genre} {request.parameters.mood} {request.parameters.voice_type}",
            "title": request.parameters.prompt[:80], 
            "customMode": True,
            "instrumental": False,
            "model": "V5",
            "callBackUrl": "https://example.com/api/suno-webhook"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status() 
            data = response.json()
            
            # --- THE FIX IS HERE ---
            # Suno returns HTTP 200 even for errors, so we must check its internal "code"
            if data.get("code") != 200:
                return {
                    "status": "FAILED",
                    "error": data.get("msg", "Unknown Suno API Error")
                }
            
            # Safely extract the taskId whether Suno nested it or not
            task_id_from_suno = None
            if isinstance(data.get("data"), dict):
                task_id_from_suno = data["data"].get("taskId") or data["data"].get("task_id")
            if not task_id_from_suno:
                task_id_from_suno = data.get("taskId") or data.get("id") or data.get("data")
            
            return {
                "status": "PENDING", 
                "task_id": task_id_from_suno,
                "raw_response": data 
            }
            
        except requests.exceptions.RequestException as e:
            # Capture the exact error message Suno sends back
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - {e.response.text}"
            return {
                "status": "FAILED",
                "error": error_msg
            }
from .base_strategy import SongGeneratorStrategy
from music.models import SongGenerationRequest
import uuid

class MockSongGeneratorStrategy(SongGeneratorStrategy):
    """Mock strategy that returns deterministic, fake data."""
    
    def generate(self, request: SongGenerationRequest) -> dict:
        # Generate a fake taskId and dummy output
        fake_task_id = str(uuid.uuid4())
        
        return {
            "taskId": fake_task_id,
            "status": "SUCCESS",
            "audioUrl": "http://example.com/dummy_audio_file.mp3",
            "message": f"Successfully mocked generation for prompt: {request.parameters.prompt}"
        }
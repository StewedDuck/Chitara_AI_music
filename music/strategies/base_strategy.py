from abc import ABC, abstractmethod
from music.models import SongGenerationRequest

class SongGeneratorStrategy(ABC):
    """Abstract Base Class for song generation strategies."""
    
    @abstractmethod
    def generate(self, request: SongGenerationRequest) -> dict:
        """
        Generates a song based on the provided request data.
        Returns a dictionary containing the result or task ID.
        """
        pass
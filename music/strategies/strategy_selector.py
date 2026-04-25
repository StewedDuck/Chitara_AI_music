# strategy_selector.py
from django.conf import settings
from .base_strategy import SongGeneratorStrategy
from .mock_strategy import MockSongGeneratorStrategy
from .suno_strategy import SunoSongGeneratorStrategy

def get_song_generator_strategy() -> SongGeneratorStrategy:
    """
    Factory function to return the correct strategy based on Django settings.
    """
    # Defaults to 'mock' if not set
    strategy_name = getattr(settings, 'GENERATOR_STRATEGY', 'mock').lower()
    
    if strategy_name == 'suno':
        return SunoSongGeneratorStrategy()
    
    return MockSongGeneratorStrategy()
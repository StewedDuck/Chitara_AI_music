# Chitara AI Music – Advanced AI Music Composer 🎸

[cite_start]Chitara AI Music is a full-stack Django application that empowers creators to compose original music tracks using the **Suno AI API**. [cite_start]Built with a focus on clean software architecture, the project utilizes the **Strategy Design Pattern** to provide a flexible and extensible foundation for AI music generation.

## ✨ Features

* [cite_start]**AI Song Generation**: Harnesses Suno AI V5 to generate high-quality audio based on user prompts, genre, and mood[cite: 10, 16].
* [cite_start]**Strategy Design Pattern**: Easily toggle between real AI generation and a cost-free mock mode for development.
* [cite_start]**Real-time Polling**: An asynchronous frontend mechanism that automatically tracks generation status and reveals the player once the track is ready.
* [cite_start]**Seamless Google Authentication**: Integrated one-click login using `django-allauth`[cite: 8, 10].
* [cite_start]**Music Library (CRUD)**: Full control over your creations—rename, delete, and manage your history[cite: 15, 23].
* [cite_start]**Permanent Sharing**: Generate unique, public links for any song to share with your audience[cite: 15, 22].


## Architecture: Strategy Pattern

[cite_start]The core logic follows the **Strategy Pattern**, allowing the system to switch generation engines without modifying the underlying business logic.

* [cite_start]**`SongGeneratorStrategy`**: The abstract base class defining the required interface[cite: 11, 13].
* [cite_start]**`SunoSongGeneratorStrategy`**: Communicates with the external Suno API for real music production[cite: 10, 16].
* [cite_start]**`MockSongGeneratorStrategy`**: Returns deterministic dummy data, preserving API credits during UI/UX testing[cite: 10].
* [cite_start]**`StrategySelector`**: A factory that reads your local settings to determine which engine to use[cite: 10].


## 🚀 Getting Started

### 1. Installation
```bash
# Clone the repo
git clone [https://github.com/StewedDuck/Chitara_AI_music.git](https://github.com/StewedDuck/Chitara_AI_music.git)
cd Chitara_AI_music

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Install Django and dependencies
pip install django requests django-allauth
```
```bash
### 2. Database Setup
Bash
python manage.py makemigrations
python manage.py migrate
```
```bash
### 3. Strategy Configuration
Edit config/settings.py to configure your generation engine:

Python
# Choose: 'suno' or 'mock'
GENERATOR_STRATEGY = 'suno' 

# Your Suno API Key (keep this private!)
SUNO_API_KEY = 'your-key-here'
```

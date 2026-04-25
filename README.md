# Chitara AI Music – Advanced AI Music Composer 🎸

Chitara AI Music is a full-stack Django application that empowers creators to compose original music tracks using the **Suno AI API**. Built with a focus on clean software architecture, the project utilizes the **Strategy Design Pattern** to provide a flexible and extensible foundation for AI music generation.

## ✨ Features

* **AI Song Generation**: Harnesses Suno AI V5 to generate high-quality audio based on user prompts, genre, and mood.
* **Strategy Design Pattern**: Easily toggle between real AI generation and a cost-free mock mode for development.
* **Real-time Polling**: An asynchronous frontend mechanism that automatically tracks generation status and reveals the player once the track is ready.
* **Seamless Google Authentication**: Integrated one-click login using `django-allauth`.
* **Music Library (CRUD)**: Full control over your creations—rename, delete, and manage your history.
* **Permanent Sharing**: Generate unique, public links for any song to share with your audience.


## Architecture: Strategy Pattern

* The core logic follows the **Strategy Pattern**, allowing the system to switch generation engines without modifying the underlying business logic.

* **`SongGeneratorStrategy`**: The abstract base class defining the required interface.
* **`SunoSongGeneratorStrategy`**: Communicates with the external Suno API for real music production.
* **`MockSongGeneratorStrategy`**: Returns deterministic dummy data, preserving API credits during UI/UX testing.
* **`StrategySelector`**: A factory that reads your local settings to determine which engine to use.


## 🚀 Getting Started

### 1. Installation
```bash
# Clone the repo
git clone [https://github.com/StewedDuck/Chitara_AI_music.git]
cd Chitara_AI_music

# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Install Django and dependencies
pip install -r requirements.txt
```

### 2. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Strategy Configuration
```bash
Edit config/settings.py to configure your generation engine:

Python
# Choose: 'suno' or 'mock'
GENERATOR_STRATEGY = 'suno' 

# Your Suno API Key
SUNO_API_KEY = 'your-key-here'
```

## 📂 Technical Implementation Details

* Persistence: The system captures the nested streamAudioUrl from the Suno API response and stores it in the Song model, ensuring your library is permanent.

* Asynchronous Polling: The frontend uses a 10-second JavaScript interval to poll the /music/api/status/ endpoint for any "DRAFT" songs until they are marked as "SUCCESS".

* Direct Login: Configured with SOCIALACCOUNT_LOGIN_ON_GET = True to bypass confirmation screens and go straight to Google Account selection.

## 🛠️ Built With

* Django: Core Backend Framework.

* Bootstrap 5: Modern, responsive UI.

* Suno AI API: AI Music Engine.

* Django-allauth: Authentication & Social login.
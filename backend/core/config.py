import os
from dotenv import load_dotenv

# Load the same .env file used by the Next.js frontend
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=dotenv_path)

class Settings:
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "3307"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "ai_eye_contact")
    
    # Paths
    TEMP_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "temp_audio")
    TEMP_FRAMES_DIR = os.path.join(os.path.dirname(__file__), "..", "temp_frames")
    PROCESSED_FRAMES_DIR = os.path.join(os.path.dirname(__file__), "..", "processed_frames")
    FINISHED_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "finished")

    # Video settings
    OUTPUT_FPS: int = 30

settings = Settings()

# Ensure directories exist
os.makedirs(settings.TEMP_AUDIO_DIR, exist_ok=True)
os.makedirs(settings.TEMP_FRAMES_DIR, exist_ok=True)
os.makedirs(settings.PROCESSED_FRAMES_DIR, exist_ok=True)
os.makedirs(settings.FINISHED_DIR, exist_ok=True)

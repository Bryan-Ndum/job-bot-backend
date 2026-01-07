import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    CLOUD_MODE: bool = os.getenv("CLOUD_MODE", "false").lower() == "true"
    
    # Job board credentials (optional)
    INDEED_EMAIL: str = os.getenv("INDEED_EMAIL", "")
    INDEED_PASSWORD: str = os.getenv("INDEED_PASSWORD", "")
    LINKEDIN_EMAIL: str = os.getenv("LINKEDIN_EMAIL", "")
    LINKEDIN_PASSWORD: str = os.getenv("LINKEDIN_PASSWORD", "")

settings = Settings()

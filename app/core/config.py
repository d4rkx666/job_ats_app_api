from pydantic_settings import BaseSettings
from typing import Dict

class Settings(BaseSettings):
   # App settings
   app_name: str = "Job ATS App"
   app_version: str = "1.0.0"
   app_description: str = "An AI-powered resume optimization service."

   #variables
   app_lang_en: str
   app_lang_es: str

   #type of responses
   type_response: Dict[str, str]

   status_response: Dict[str, str]

   # Server settings
   host: str = "0.0.0.0"  # Default to localhost
   port: int = 8000  # Default port

   # CORS settings
   cors_origins: list[str] = [
   "http://localhost:3000",  # React frontend
   ]

   # OpenAI settings
   openai_api_key: str

   # Firebase settings
   firebase_credentials: str

   class Config:
      env_file = ".env"

settings = Settings()
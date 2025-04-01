from pydantic_settings import BaseSettings
from typing import Dict

class Settings(BaseSettings):
   # App settings
   app_name: str
   app_version: str
   app_description: str

   #variables
   app_lang_en: str
   app_lang_es: str

   # Service config
   app_free_initial_improvements: int
   app_free_initial_creations: int
   app_free_model: str
   app_pro_model: str
   app_business_model: str

   # AI config
   app_ai_c1_role_system_en: str
   app_ai_c1_role_user_en: str
   app_ai_c1_role_system_es: str
   app_ai_c1_role_user_es: str

   # Type of responses
   type_response: Dict[str, str]
   status_response: Dict[str, str]

   # Server settings
   host: str = "0.0.0.0"
   port: int = 8000

   # CORS settings
   cors_origins: str

   # OpenAI settings
   openai_api_key: str

   # Firebase settings
   firebase_credentials: str

   class Config:
      env_file = ".env"

settings = Settings()
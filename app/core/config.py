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
   app_free_initial_credits: int
   app_pro_reset_credits: int

   # Trial DAYS
   app_trial_days: int

   # For cron
   app_env_prod: bool

   # Models
   app_free_model: str
   app_pro_model: str
   app_business_model: str

   # Server settings
   host: str = "0.0.0.0"
   port: int = 8000

   # CORS settings
   cors_origins: str

   # OpenAI settings
   openai_api_key: str

   # Firebase settings
   firebase_credentials: str

   # Stripe keys
   stripe_secret_key: str
   stripe_signing_secret_key: str
   
   stripe_success_endpoint: str
   stripe_cancel_endpoint: str
   stripe_return_session_url: str

   
   stripe_price_id: str
   stripe_product_id: str

   cron_secret: str

   class Config:
      env_file = ".env"

settings = Settings()
import stripe
from app.core.config import settings
from fastapi import HTTPException

def initialize_stripe():
   stripe.api_key = settings.stripe_secret_key
   stripe.max_network_retries = 3

   # Verify the API key works
   try:
      stripe.Account.retrieve()  # Simple API call to verify connection
   except stripe.error.AuthenticationError as e:
      return None
   
   return stripe

# Initialize Firestore and export the `db` variable
stripe = initialize_stripe()
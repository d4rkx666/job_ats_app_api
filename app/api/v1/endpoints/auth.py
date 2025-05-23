from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from app.core.security import get_current_user
from app.models.schemas import InsertDataRequest
from firebase_admin import auth, firestore
from app.services.firebase_service import db  # Import the Firestore client
from app.core.config import settings
from datetime import datetime
from dateutil.relativedelta import relativedelta

router = APIRouter()

## !!!! NOT IN USE !!!!
"""@router.post("/login")
async def login(login_request: LoginRequest):
   try:
      # Verify the user's email and password using Firebase Admin SDK
      user = auth.sign_in_with_email_and_password(login_request.email, login_re)

      # Generate a Firebase ID token (or custom token)
      custom_token = auth.create_custom_token(user.uid)

      # Get user data from Firestore
      db = firestore.client()
      user_doc = db.collection("users").document(user.uid).get()
      if not user_doc.exists:
         raise HTTPException(status_code=404, detail="Email or password incorrect. Please try again.")

      user_data = user_doc.to_dict()

      # Return the token and user data
      return {
         "auth": True,
         "token": custom_token,
         "user": user_data,
      }
   except auth.UserNotFoundError:
      raise HTTPException(status_code=404, detail="Email or password incorrect. Please try again.")
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))

"""
@router.post("/signup")
async def signup(signup_request: InsertDataRequest):
   try:
      # Creating the user in Firebase Authentication
      user = auth.create_user(
         email=signup_request.email,
         password=signup_request.password
      )

      # Adding extra data to Firestore
      configs = {
         "name": signup_request.name,
         "email": signup_request.email,
         "country": signup_request.country,
         "role": "user",  # Default role
         "createdAt": datetime.now(),
         "is_active": True,  # Default status
         "usage": {
            "current_credits": settings.app_free_initial_credits,  # Free tier default
            "total_credits": settings.app_free_initial_credits,
            "used_credits": 0,
            "last_reset": datetime.now(),
            "next_reset": datetime.now() + relativedelta(months=1),
            "actions": {
               "keyword_optimizations": 0,
               "resume_optimizations": 0,
               "resume_creations": 0,
            }
         },
         "profile":{
            "contact":{
               "name": signup_request.name,
               "email": signup_request.email,
            }
         },
         "subscription": {
            "plan": "free",
            "status": "active",
            "stripe_id": "",
            "current_period_start": None,
            "current_period_end": None,
            "payment_method": "None",
            "history": []
         },
         "features": {
            "priority_support": False,
         }
      }

      # Save the default data to Firestore under the user's UID
      db.collection("users").document(user.uid).set(configs)

      # Return the user UID and other details
      return {
         "status": "success",
         "type": "create_user",
         "message": "User created successfully",
         "user": {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "phone_number": user.phone_number,
         },
      }
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
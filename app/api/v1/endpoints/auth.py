from fastapi import APIRouter, HTTPException, Body, Response
from app.models.schemas import InsertDataRequest
from firebase_admin import auth
from app.services.firebase_service import db  # Import the Firestore client
from app.core.config import settings
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta

router = APIRouter()

@router.post("/auth")
async def login(response: Response, token: str = Body(embed=True)):
   try:
      expires_in = timedelta(hours=1)
      session_cookie = auth.create_session_cookie(token, expires_in=expires_in)

      # PRIVATE COOKIE
      response.set_cookie(
         key="session",
         value=session_cookie,
         httponly=True,
         secure=True,
         samesite="None",
         max_age=int(expires_in.total_seconds()),
         path="/"
      )

      # PUBLIC COOKIE
      response.set_cookie(
         key="logged", 
         value="true", 
         httponly=False,
         max_age=int(expires_in.total_seconds())
      )

      return {
         "success": True
      }
   except Exception as e:
      raise HTTPException(status_code=401, detail="Email or password incorrect. Please try again.")

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
from fastapi import HTTPException
from app.services.firebase_service import db
from firebase_admin import firestore
from datetime import datetime


async def setChatGptError(type_error: str, data: str, user_id: str):
   try:
      error_ref = db.collection("errors").document("chatgpt")

      #Create dict to add
      inserting_data = {
         "type_error": type_error,
         "data": data,
         "createdAt": datetime.now(),
      }

      # Add the new improvement to the array
      error_ref.update({
         user_id: firestore.ArrayUnion([inserting_data]),
      })
      
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
   

async def setError(message: str):
   try:
      error_ref = db.collection("errors").document("error")

      #Create dict to add
      inserting_data = {
         "type_error": "runtime",
         "exception": message,
         "createdAt": datetime.now(),
      }

      # Add the new improvement to the array
      error_ref.update({
         "general_error": firestore.ArrayUnion([inserting_data]),
      })
      
   except Exception as e:
      print(e)
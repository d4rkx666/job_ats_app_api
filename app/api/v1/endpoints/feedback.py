from fastapi import APIRouter, Depends, HTTPException
from app.services.firebase_service import db  # Import the Firestore client
from app.models.schemas import FeedbackRequest
from app.core.security import get_current_user
from datetime import datetime

router = APIRouter()

@router.post("/feedback")
async def send_feedback(feedback_request: FeedbackRequest, user: dict = Depends(get_current_user)):
   try:
      user_ref = db.collection("users").document(user["uid"])
      user_doc = user_ref.get()

      if user_doc.exists:

         #Create dict to add
         inserting_data = {
            "star": feedback_request.stars,
            "comments": feedback_request.comment,
            "createdAt": datetime.now(),
         }

         # Add the new improvement to the array
         user_ref.update({
            "feedback": inserting_data,
         })
      else:
         raise HTTPException(status_code=404, detail="User not found")

      return {"success": True}
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))


async def add_improvement(user_ref: dict, job_title: str, job_description: str, new_improvement: str):
   try:

      #Create dict to add
      inserting_data = {
         "id": str(uuid.uuid4()),
         "job_title": job_title,
         "job_description": job_description,
         "ai_improvements": new_improvement,
         "createdAt": datetime.now(),
         "status": "completed"
      }

      # Add the new improvement to the array
      user_ref.update({
         "improvements": firestore.ArrayUnion([inserting_data]),
         "settings.resumeImprovements": firestore.Increment(1),
      })

      return {
         "status": "success",
         "type": "add_improvement",
         "message": "Improvement added successfully",
      }
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))


async def has_improvements(user_id: str):
   try:
      user_ref = db.collection("users").document(user_id)
      user_doc = user_ref.get()
      hasImprovementsLeft = False

      if user_doc.exists:
         current_user = user_doc.to_dict()
         settings = current_user.get("settings", {})
         resume_improvements = settings.get("resumeImprovements", 10)
         maximum_improvements = settings.get("maximumImprovements", 10)

         if resume_improvements <= maximum_improvements:
            hasImprovementsLeft = True
      else:
         raise HTTPException(status_code=404, detail="User not found")

      return {"hasImprovementsLeft": hasImprovementsLeft, "user_ref": user_ref}
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))

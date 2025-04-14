from fastapi import HTTPException
from firebase_admin import firestore
from app.services.firebase_service import db
from app.core.config import settings
from app.services.db_variables import get_costs
import uuid
from datetime import datetime
from dateutil.relativedelta import relativedelta

async def getUserData(user_id: str):
   try:
      user_ref = db.collection("users").document(user_id)
      user_doc = user_ref.get()

      # Info needed
      currentPlan = "free"

      if user_doc.exists:
         current_user = user_doc.to_dict()

         # Other info
         suscription = current_user.get("subscription", {})
         profile = current_user.get("profile", {})
         creations = current_user.get("creations", [])
 
         # Get plan
         currentPlan = suscription.get("plan", "free")
      else:
         raise HTTPException(status_code=404, detail="User not found")

      return {"creations": creations, "currentPlan": currentPlan, "profile": profile, "user_ref": user_ref}
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
         "current_version": "free",
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
         "method": "add_improvement",
         "type": "add_improvement",
         "message": "Improvement added successfully",
      }
   except Exception as e:
      raise HTTPException(status_code=501, detail=str(e))
   

async def add_keywords(user_ref: dict, job_title: str, job_description: str, jd_lang: str, keywords: dict):
   try:

      #Create dict to add
      inserting_data = {
         "id": str(uuid.uuid4()),
         "job_title": job_title,
         "job_description": job_description,
         "job_description_lang": jd_lang,
         "keywords": keywords,
         "createdAt": datetime.now(),
         "status": "draft"
      }

      # Add the new improvement to the array
      user_ref.update({
         "creations": firestore.ArrayUnion([inserting_data])
      })

      return {
         "status": "success",
         "method": "add_keywords",
         "type": "add_keywords",
         "idInserted": inserting_data["id"],
         "message": "Improvement added successfully",
      }
   except Exception as e:
      raise HTTPException(status_code=501, detail=str(e))
   

async def update_keywords_draft(user_ref: dict, creations: dict, idDraft: str, keywords: dict):
   try:
      success = True
      creation_index = next((i for i, c in enumerate(creations) if c.get("id") == idDraft), None)
        
      if creation_index is not None:
         # Update the specific creation's keywords
         creations[creation_index]["keywords"] = keywords

         # Push the update to Firestore
         user_ref.update({"creations": creations})
      else:
         success = False

      return {
         "success": success,
      }
   except Exception as e:
      raise HTTPException(status_code=501, detail=str(e))
   

   
async def update_creation(user_ref: dict, resume: str, ats_analysis: dict, ats:dict, keywords: list, creations: dict, idDraft: str):

   try:
      success = True
      creation_index = next((i for i, c in enumerate(creations) if c.get("id") == idDraft), None)

      if creation_index is not None:
         creations[creation_index]["status"] = "created"
         creations[creation_index]["resume"] = resume
         creations[creation_index]["keywords"] = keywords
         creations[creation_index]["ats"] = ats
         creations[creation_index]["ats_analysis"] = ats_analysis
         

         # Push the update to Firestore
         user_ref.update({"creations": creations})
      else:
         success = False

      return {
         "success": success,
      }
   except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
   

async def update_resume(user_ref: dict, resume: str, creations: dict, idDraft: str):

   try:
      success = True
      creation_index = next((i for i, c in enumerate(creations) if c.get("id") == idDraft), None)

      if creation_index is not None:
         creations[creation_index]["resume"] = resume

         # Push the update to Firestore
         user_ref.update({"creations": creations})
      else:
         success = False

      return {
         "success": success,
      }
   except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
   



async def deduct_credits(user_id: str, action: str) -> bool:
   try:
      user_ref = db.collection("users").document(user_id)

      # get cost vars:
      cost = get_costs()

      # Define credit costs
      CREDIT_COSTS = {
         "keyword_optimizations": cost.get("keyword_extraction"),
         "resume_optimizations": cost.get("resume_optimization"),
         "resume_creations": cost.get("resume_creation"),
         "resume_ats_analyzation": cost.get("ats_analysis"),
      }
      
      @firestore.transactional
      def process(transaction):
         user = user_ref.get(transaction=transaction).to_dict()
         current_credits = user.get("usage", {}).get("current_credits", 0)
         cost = CREDIT_COSTS[action]
         
         if current_credits >= cost:
            transaction.update(user_ref, {
                  "usage.current_credits": firestore.Increment(-cost),
                  "usage.used_credits": firestore.Increment(cost),
                  f"usage.actions.{action}": firestore.Increment(1)
            })
            return True
         return False
      
      return process(db.transaction())
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))


def reset_monthly_credits():
   users_ref = db.collection("users")
   
   for user in users_ref.stream():
      user_data = user.to_dict()
      next_reset = user_data.get("usage", {}).get("next_reset")
      
      # Reset if next_reset is past or doesn't exist
      if not next_reset or datetime.now() > next_reset:
         plan = user_data.get("subscription", {}).get("plan", "free")
         new_credits = settings.app_free_initial_credits if plan == "free" else settings.app_pro_reset_credits if plan == "pro" else 0
         
         # Update user with reset credits
         user.reference.update({
               "usage.current_credits": new_credits,
               "usage.last_reset": datetime.now(),
               "usage.next_reset": datetime.now() + relativedelta(month=1)
         })
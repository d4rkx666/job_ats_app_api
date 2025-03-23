from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.services.firebase_service import db  # Import the Firestore client
from firebase_admin import firestore
from app.models.schemas import ResumeRequest, OptimizedResumeResponse
from app.services.openai_service import optimize_resume
from app.core.security import get_current_user
from PyPDF2 import PdfReader
import io
import uuid
from datetime import datetime
import re

router = APIRouter()

@router.post("/optimize-resume", response_model = OptimizedResumeResponse)
async def optimize_resume_endpoint(resume: UploadFile = File(...), job_title: str = Form(...), job_description: str = Form(...), lang: str = Form(...),user: dict = Depends(get_current_user)):

   try:
      # Validate file type
      allowed_file_types = ["application/pdf"]
      if resume.content_type not in allowed_file_types:
         raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only PDF files are allowed."
         )

      # Validate file size (e.g., 5MB limit)
      max_file_size = 5 * 1024 * 1024  # 5MB
      if resume.size > max_file_size:
         raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the limit of {max_file_size / 1024 / 1024}MB."
         )

      # Convert PDF to Text
      resume_content = await resume.read()
      # Wrap the bytes in a file-like object using BytesIO
      resume_file_like = io.BytesIO(resume_content)

      reader = PdfReader(resume_file_like)
      resume_text = ""
      for page in reader.pages:
         resume_text += page.extract_text()

      # Check if has improvements left
      validate_user_data = await getUserData(user["uid"])
      if(validate_user_data["hasImprovementsLeft"]):
         # Clean job description
         job_description = clean_text(job_description)
         new_resume = await optimize_resume(resume_text, job_title, job_description, lang, validate_user_data["currentPlan"])
         await add_improvement(validate_user_data["user_ref"], job_title, job_description, new_resume["optimized_resume"])

         return new_resume
      else: 
         raise HTTPException(status_code=203, detail="You have not improvements left.")

      
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
         "type": "add_improvement",
         "message": "Improvement added successfully",
      }
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))


async def getUserData(user_id: str):
   try:
      user_ref = db.collection("users").document(user_id)
      user_doc = user_ref.get()

      # Info needed
      hasImprovementsLeft = False
      currentPlan = "free"

      if user_doc.exists:
         current_user = user_doc.to_dict()
         settings = current_user.get("settings", {})
         suscription = current_user.get("suscription", {})

         # Calculate improvements left
         resume_improvements = settings.get("resumeImprovements", 10)
         maximum_improvements = settings.get("maximumImprovements", 10)

         # Get plan
         currentPlan = suscription.get("plan", "free")


         # Validate improvements left
         if resume_improvements < maximum_improvements:
            hasImprovementsLeft = True
      else:
         raise HTTPException(status_code=404, detail="User not found")

      return {"hasImprovementsLeft": hasImprovementsLeft, "currentPlan": currentPlan, "user_ref": user_ref}
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))

def clean_text(text):
   # Remove extra spaces (including tabs and multiple spaces)
   text = re.sub(r'\s+', ' ', text)
   
   # Remove line breaks
   text = text.replace('\n', ' ')
   
   # Trim leading and trailing spaces
   text = text.strip()
   
   return text
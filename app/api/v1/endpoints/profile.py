from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.firebase_service import db  # Import the Firestore client
from app.models.schemas import ProfileRequest, ProfilePersonalInformationRequest, ProfileSkillsRequest
from app.core.security import get_current_user

router = APIRouter()

@router.post("/update-personal-information")
async def update_personal_information_endpoint(profile_request: ProfilePersonalInformationRequest,user: dict = Depends(get_current_user)):

   try:
      user_ref = db.collection("users").document(user["uid"])

      # Add the new improvement to the array
      user_ref.set({
         "phone": profile_request.phone,
         "email": profile_request.email,
         "linkedin": profile_request.linkedin,
         "website": profile_request.website,
      },merge=True)

      return {
         "status": "success",
         "type": "update_personal_information",
         "message": "Personal information updated successfully",
      }
   except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))



@router.post("/update-skills")
async def update_personal_information_endpoint(profile_request: ProfileSkillsRequest,user: dict = Depends(get_current_user)):

   try:
      user_ref = db.collection("users").document(user["uid"])

      # Add the new improvement to the array
      user_ref.update({
         "profile.skills": profile_request.skills,
         "profile.education": [],
         "profile.jobs": [],
         "profile.projects": [],
      })

      return {
         "status": "success",
         "type": "update_skills",
         "message": "Skills information updated successfully",
      }
   except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-profile")
async def update_profile_endpoint(profile_request: ProfileRequest,user: dict = Depends(get_current_user)):

   try:
      user_ref = db.collection("users").document(user["uid"])

      #Create dict to add
      inserting_data = {
         "skills": [],
         "education": [model_to_dict(edu) for edu in profile_request.educations],
         "jobs": [model_to_dict(job) for job in profile_request.jobs],
         "projects": [model_to_dict(proj) for proj in profile_request.projects],
      }

      # Add the new improvement to the array
      user_ref.set({
         "profile": inserting_data,
      },merge=True)

      return {
         "status": "success",
         "type": "update_profile",
         "message": "Profile updated successfully",
      }
   except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
   

# Convert Pydantic models to dictionaries
def model_to_dict(model):
   if isinstance(model, BaseModel):
         return model.model_dump()
   return model
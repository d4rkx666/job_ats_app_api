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

      #Create dict to add
      inserting_data = {
         "phone": profile_request.phone,
         "email": profile_request.email,
         "linkedin": profile_request.linkedin,
         "website": profile_request.website,
      }

      # Add the new improvement to the array
      user_ref.update({
         "profile.contact":inserting_data
      })

      return {
         "success": True,
         "type_error": "",
      }
   except Exception as e:
      return {
         "success": False,
         "type_error": "not_saved",
      }



@router.post("/update-skills")
async def update_personal_information_endpoint(profile_request: ProfileSkillsRequest,user: dict = Depends(get_current_user)):

   try:
      user_ref = db.collection("users").document(user["uid"])

      # Add the new improvement to the array
      user_ref.update({
         "profile.skills": profile_request.skills,
      })

      return {
         "success": True,
         "type_error": "",
      }
   except Exception as e:
      return {
         "success": False,
         "type_error": "not_saved",
      }


@router.post("/update-profile")
async def update_profile_endpoint(profile_request: ProfileRequest,user: dict = Depends(get_current_user)):

   try:
      user_ref = db.collection("users").document(user["uid"])

      #Create dict to add
      inserting_data = {
         "education": [model_to_dict(edu) for edu in profile_request.educations],
         "jobs": [model_to_dict(job) for job in profile_request.jobs],
         "projects": [model_to_dict(proj) for proj in profile_request.projects],
      }

      # Add the new improvement to the array
      user_ref.set({
         "profile": inserting_data,
      },merge=True)

      return {
         "success": True,
         "type_error": "",
      }
   except Exception as e:
      return {
         "success": False,
         "type_error": "not_saved",
      }
   

# Convert Pydantic models to dictionaries
def model_to_dict(model):
   if isinstance(model, BaseModel):
         return model.model_dump()
   return model
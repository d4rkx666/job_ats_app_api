from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.models.schemas import OptimizedResumeResponse, KeywordOptimizationRequest, OptimizedKeywordsResponse
from app.services.openai_service import optimize_resume
from app.core.security import get_current_user
from app.services.user_actions_manager import getUserData, add_improvement, add_keywords, update_score, deduct_credits
from PyPDF2 import PdfReader
from app.utils.text import clean_text, extract_keywords, calculate_job_match, format_resume_to_plain_text
import io

router = APIRouter()

@router.post("/optimize-resume", response_model = OptimizedResumeResponse)
async def optimize_resume_endpoint(resume: UploadFile = File(...), job_title: str = Form(...), job_description: str = Form(...), lang: str = Form(...),user: dict = Depends(get_current_user)):

   # Current function for credits
   current_function = "resume_optimizations"

   try:
      # Validate file type
      allowed_file_types = ["application/pdf"]

      # Response
      response = {
         "optimized_resume": "",
         "success": True,
         "type_error": ""
      }
      if resume.content_type not in allowed_file_types:
         response["success"] = False
         response["type_error"] = "invalid_file_type"
         
         return response

      # Validate file size (e.g., 5MB limit)
      max_file_size = 5 * 1024 * 1024  # 5MB
      if resume.size > max_file_size:
         response["success"] = False
         response["type_error"] = "file_size_exceeded"
         
         return response

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

      
      # Validate remaining credits
      hasCredits = await deduct_credits(user["uid"], current_function)
      if(hasCredits):
         # Clean job description
         job_description = clean_text(job_description)


         #Get optimized suggestions
         response["optimized_resume"] = await optimize_resume(resume_text, job_title, job_description, lang, validate_user_data["currentPlan"])

         # Add suggestions to firebase
         await add_improvement(validate_user_data["user_ref"], job_title, job_description, response["optimized_resume"])

         return response
      else: 
         response["success"] = False
         response["type_error"] = "no_credits_left"

         return response

      
   except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
   

@router.post("/extract-keywords", response_model = OptimizedKeywordsResponse)
async def extract_keywords_endpoint(request: KeywordOptimizationRequest, user: dict = Depends(get_current_user)):

   # Current function for credits
   current_function = "keyword_optimizations"

   try:

      # Get user data
      validate_user_data = await getUserData(user["uid"])
      
      # Validate subscription
      isProUser = False

      if(validate_user_data["currentPlan"] == "pro"):
         isProUser = True

      # Init response
      response = {
         "keywords": [],
         "score": 0,
         "success": True,
         "type_error": ""
      }

      # Validate if draft
      if(request.isDraft):
         # Validate credits before updating
         hasCredits = await deduct_credits(user["uid"], current_function)
         if(hasCredits):
            newData = await update_score(validate_user_data["user_ref"], validate_user_data["creations"], request.idDraft, validate_user_data["profile"])
            response["score"] = newData["score"]
            response["keywords"] = newData["keywords"]
         else:
            response["success"] = False
            response["type_error"] = "no_credits_left"
            return response
      else:
         # Check request type
         match request.type:
            case "free":
               # Validate credits before updating
               hasCredits = await deduct_credits(user["uid"], current_function)
               if(hasCredits):
                  # Extract free no matter the user
                  response["keywords"] = extract_keywords(request.job_description, request.lang)
                  profile = format_resume_to_plain_text(validate_user_data["profile"])
                  response["score"] = calculate_job_match(profile, response["keywords"])
               else:
                  response["success"] = False
                  response["type_error"] = "no_credits_left"
                  return response
               
            #case "pro":
               # Extract
               #if(isProUser):
                  # Extract with AI
            case _:
               response["success"] = False
               response["type_error"] = "plan_not_found"
               return response

         # Save data to firestore
         await add_keywords(validate_user_data["user_ref"], request.job_title, request.job_description, response["keywords"], response["score"])

      return OptimizedKeywordsResponse(**response)

      
   except Exception as e:
         raise HTTPException(status_code=501, detail=str(e))
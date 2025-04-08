from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.models.schemas import OptimizedResumeResponse, KeywordOptimizationRequest, OptimizedKeywordsResponse, CreateResumeRequest
from app.services.openai_service import optimize_resume, create_resume, extract_keywords_ai, calculate_ats_score
from app.core.security import get_current_user
from app.services.user_actions_manager import getUserData, add_improvement, add_keywords, update_score, deduct_credits,update_draft
from app.services.rules_management import get_templates, get_keywords_rules
from app.services.log_saver import setChatGptError
from PyPDF2 import PdfReader
from app.utils.text import clean_text, to_json
import io

router = APIRouter()

@router.post("/optimize-resume", response_model = OptimizedResumeResponse)
async def optimize_resume_endpoint(resume: UploadFile = File(...), job_title: str = Form(...), job_description: str = Form(...), lang: str = Form(...),user: dict = Depends(get_current_user)):

   # Current function for credits
   current_function = "resume_optimizations"

   # Response INIT
   response = {
      "optimized_resume": "",
      "success": True,
      "type_error": ""
   }

   try:
      # Validate file type
      allowed_file_types = ["application/pdf"]

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
   

@router.post("/extract-keywords")
async def extract_keywords_endpoint(request: KeywordOptimizationRequest, user: dict = Depends(get_current_user)):

   # Current function for credits
   current_function = "keyword_optimizations"

   # Init response
   response = {
      "keywords": [],
      "idDraft": "",
      "success": True,
      "type_error": ""
   }

   try:

      # Get user data
      validate_user_data = await getUserData(user["uid"])
      
      # Validate subscription
      isProUser = False

      if(validate_user_data["currentPlan"] == "pro"):
         isProUser = True

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

         # Get rules
         manageRules= await get_keywords_rules()

         # Validate credits
         hasCredits = await deduct_credits(user["uid"], current_function)
         if(hasCredits):
            # Extract with AI
            response["keywords"] = await extract_keywords_ai(clean_text(request.job_description), manageRules, validate_user_data["currentPlan"])
            json_str = to_json(response["keywords"])
            
            if(json_str):
               response["keywords"] = json_str["keywords"]
            else:
               response["success"] = False
               response["type_error"] = "incorrect_json"
               setChatGptError(response["type_error"], response["keywords"], user["uid"])
               return response
               

         # Save data to firestore
         insert = await add_keywords(validate_user_data["user_ref"], request.job_title, request.job_description, response["keywords"])
         response["idDraft"] = insert["idInserted"]

      return response

      
   except Exception as e:
      raise HTTPException(status_code=501, detail=str(e))
   


@router.post("/create-resume")
async def create_resume_endpoint(request: CreateResumeRequest, user: dict = Depends(get_current_user)):

   # Current function for credits
   current_function = "resume_creations"

   # Init response
   response = {
      "resume": "",
      "ats": {},
      "success": True,
      "type_error": ""
   }

   try:
      # Get user data
      validate_user_data = await getUserData(user["uid"])

      # Validate subscription
      isProUser = False
      if(validate_user_data["currentPlan"] == "pro"):
         isProUser = True

      # Get templates
      manageTemplate = await get_templates()
      template = manageTemplate.get("templates",{}).get(request.template,{})
      
      # Validates if the template is pro and the user is not pro
      if(template.get("isPro", True)):
         if(not isProUser):
            response["success"] = False
            response["type_error"] = "user_not_pro_plan"
            return response
         
         
      if(request.coverLetter):
         if(not isProUser):
            response["success"] = False
            response["type_error"] = "user_not_pro_plan"
            return response
         
      # Finds creation by ID
      creation = next(item for item in validate_user_data["creations"] if item["id"] == request.idDraft)
      #print(clean_text(creation["job_description"]))
      
      
      # Validate credits then call AI
      hasCredits = await deduct_credits(user["uid"], current_function)
      if(hasCredits):

         # Create the markdown resume
         globalRules = manageTemplate.get("global_rules",{})
         pre_processing_rules = manageTemplate.get("pre_process",{})

         # Returns markdown resume in plain text and pre processed resume in JSON
         resp = await create_resume(validate_user_data["profile"], creation["keywords"], template, pre_processing_rules, globalRules, request.lang, validate_user_data["currentPlan"])

         # Convert the pre processed resume
         pre_processed_resume_json = to_json(resp["processed_resume"])
         if(pre_processed_resume_json):
            # Plain text markdown
            response["resume"] = resp["markdown_resume"]
            
            # Update matched keywords:
            matched_keywords = pre_processed_resume_json["matched_keywords"]
            for item in creation["keywords"]:
               if item["keyword"] in matched_keywords:
                  item["matched"] = True
               else:
                  item["matched"] = False

            # Get the ATS score and tips
            ats_score_rules = manageTemplate.get("ats_completion",{})
            caculated_ats_score = await calculate_ats_score(response["resume"], creation["keywords"], ats_score_rules, validate_user_data["currentPlan"])

            # Convert to json
            caculated_ats_score_json = to_json(caculated_ats_score)

            if(caculated_ats_score_json):
               response["ats"] = caculated_ats_score_json["ats"]
               # Add the resume and matched keywords
               await update_draft(validate_user_data["user_ref"], response["resume"], response["ats"], creation["keywords"], validate_user_data["creations"], request.idDraft)
            else:
               response["success"] = False
               response["type_error"] = "incorrect_json"
               setChatGptError(response["type_error"], str(caculated_ats_score), user["uid"])
               return response
         else:
            response["success"] = False
            response["type_error"] = "incorrect_json"
            setChatGptError(response["type_error"], str(resp), user["uid"])
            return response
      else:
         response["success"] = False
         response["type_error"] = "no_credits_left"
         return response

      return response

      
   except Exception as e:
      print(e)
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.models.schemas import OptimizedResumeResponse, KeywordOptimizationRequest, SaveResumeRequest, CreateResumeRequest, ReoptimizeResumeRequest
from app.services.openai_service import optimize_resume, create_resume, extract_keywords_ai, calculate_ats_score, recalculate_ats_score
from app.core.security import get_current_user
from app.services.user_actions_manager import getUserData, add_improvement, add_keywords, update_keywords_draft, deduct_credits,update_creation, update_resume
from app.services.rules_management import get_templates, get_keywords_rules, get_improvements_rules
from app.services.log_saver import setChatGptError
from PyPDF2 import PdfReader
from app.utils.text import clean_text, process_ats_score
import io
import json

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

         # Get rules
         manageRules= await get_improvements_rules()

         #Get optimized suggestions
         json_improvements = await optimize_resume(resume_text, job_title, job_description, manageRules, validate_user_data["currentPlan"])

         response["optimized_resume"] = json.dumps(json_improvements.get("improvements",{}))

         # Add suggestions to firebase
         await add_improvement(validate_user_data["user_ref"], job_title, job_description, json_improvements.get("improvements",{}))

         return response
      else: 
         response["success"] = False
         response["type_error"] = "no_credits_left"

         return response

      
   except Exception as e:
      print(e)
   

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

      # Get rules
      manageRules= await get_keywords_rules()

      # Validate credits
      hasCredits = await deduct_credits(user["uid"], current_function)
      if(hasCredits):
         # Extract with AI
         jd_lang = ""
         json_keywords = await extract_keywords_ai(clean_text(request.job_description), manageRules, validate_user_data["currentPlan"])
         
         if(json_keywords):
            response["keywords"] = json_keywords["keywords"]
            jd_lang = json_keywords["job_description_language"]
         else:
            response["success"] = False
            response["type_error"] = "incorrect_json"
            setChatGptError(response["type_error"], response["keywords"], user["uid"])
            return response
               

         # Save data to firestore
         if(request.isDraft):
            await update_keywords_draft(validate_user_data["user_ref"], validate_user_data["creations"], request.idDraft, response["keywords"])
            response["idDraft"] = request.idDraft
         else:
            insert = await add_keywords(validate_user_data["user_ref"], request.job_title, request.job_description, jd_lang, response["keywords"])
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
         markdown_resume = await create_resume(validate_user_data["profile"], creation["keywords"],  creation["job_description_lang"], template, pre_processing_rules, globalRules, request.lang, validate_user_data["currentPlan"])

         # Plain text markdown
         response["resume"] = markdown_resume

         # Get the ATS score and tips
         ats_score_rules = manageTemplate.get("ats_completion",{})
         caculated_ats_score_json = await calculate_ats_score(response["resume"], creation["keywords"], ats_score_rules, validate_user_data["currentPlan"])

         if(caculated_ats_score_json):
            ats_score = process_ats_score(caculated_ats_score_json, creation["keywords"])
            if(ats_score):
               response["ats"] = ats_score["ats"]
               creation["keywords"] = ats_score["keywords"]
            else:
               response["success"] = False
               response["type_error"] = "ats_not_processed"
               await setChatGptError(response["type_error"], str(ats_score), user["uid"])
               return response
            # Add the resume and matched keywords
            await update_creation(validate_user_data["user_ref"], response["resume"], caculated_ats_score_json, response["ats"], creation["keywords"], validate_user_data["creations"], request.idDraft)
         else:
            response["success"] = False
            response["type_error"] = "incorrect_json"
            await setChatGptError(response["type_error"], str(caculated_ats_score_json), user["uid"])
            return response
      else:
         response["success"] = False
         response["type_error"] = "no_credits_left"
         return response

      return response

      
   except Exception as e:
      print(e)

@router.post("/reoptimize-resume")
async def reoptimize_resume_endpoint(request: ReoptimizeResumeRequest, user: dict = Depends(get_current_user)):

   # Current function for credits
   current_function = "resume_ats_analyzation"

   # Init response
   response = {
      "resume": request.resume_markdown,
      "ats": {},
      "success": True,
      "type_error": ""
   }

   try:

      # Get user data
      validate_user_data = await getUserData(user["uid"])
         
      # Finds creation by ID
      creation = next(item for item in validate_user_data["creations"] if item["id"] == request.idCreation)
      
      # Validate credits then call AI
      hasCredits = await deduct_credits(user["uid"], current_function)
      if(hasCredits):
         manageTemplate = await get_templates()

         # Get the rules and the ats score
         ats_score_rules = manageTemplate.get("ats_completion",{})
         calculated_ats_score_json = await recalculate_ats_score(response["resume"], creation["ats_analysis"], creation["keywords"], ats_score_rules, validate_user_data["currentPlan"])

         if(calculated_ats_score_json):
            # UPDATE PREVIOUS ANALYSIS:
            creation["ats_analysis"].update(calculated_ats_score_json)
            
            ats_score = process_ats_score(creation["ats_analysis"], creation["keywords"])
            if(ats_score):
               response["ats"] = ats_score["ats"]
               creation["keywords"] = ats_score["keywords"]
            else:
               response["success"] = False
               response["type_error"] = "ats_not_processed"
               await setChatGptError(response["type_error"], str(ats_score), user["uid"])
               return response
            
            # Update the resume and matched keywords
            await update_creation(validate_user_data["user_ref"], response["resume"], creation["ats_analysis"], response["ats"], creation["keywords"], validate_user_data["creations"], request.idCreation)
         else:
            response["success"] = False
            response["type_error"] = "incorrect_json"
            await setChatGptError(response["type_error"], str(calculated_ats_score_json), user["uid"])
            return response
      else:
         response["success"] = False
         response["type_error"] = "no_credits_left"
         return response
      
      return response

      
   except Exception as e:
      print(e)



@router.post("/save-resume")
async def save_resume_endpoint(request: SaveResumeRequest, user: dict = Depends(get_current_user)):

   # Init response
   response = {
      "success": True,
      "type_error": ""
   }

   try:
      # Get user data
      validate_user_data = await getUserData(user["uid"])

      # Validate subscription
      if(validate_user_data["currentPlan"] == "pro"):
         if not await update_resume(validate_user_data["user_ref"], request.resume, validate_user_data["creations"], request.idCreation):
            response["success"] = False
            response["type_error"] = "not_updated"
      else:
         response["success"] = False
         response["type_error"] = "user_not_pro_plan"

      return response

      
   except Exception as e:
      print(e)
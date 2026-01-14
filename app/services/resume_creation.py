from fastapi import HTTPException
from app.models.schemas import CreateResumeRequest
from app.services.log_saver import setChatGptError
from app.services.openai_service import calculate_ats_score, create_resume
from app.services.user_actions_manager import compensate_credits, deduct_credits, update_creation
from app.utils.text import process_ats_score


async def createResume(current_function: str, user_id: str, validate_user_data:dict, request: CreateResumeRequest, manageTemplate:dict, template: dict):
   currentStep = 2
   try:
      await deduct_credits(user_id, current_function)
      await updateViewed(validate_user_data["user_ref"], request.idDraft, current_function, validate_user_data["creations"], False)
      await updateProgress(validate_user_data["user_ref"], request.idDraft, current_function, currentStep, "preparing", validate_user_data["creations"])
         
      # Finds creation by ID
      creation = next(item for item in validate_user_data["creations"] if item["id"] == request.idDraft)

      # Create the markdown resume
      globalRules = manageTemplate.get("global_rules",{})
      pre_processing_rules = manageTemplate.get("pre_process",{})

      # Returns markdown resume in plain text and pre processed resume in JSON
      currentStep = 3
      await updateProgress(validate_user_data["user_ref"], request.idDraft, current_function, currentStep, "creating", validate_user_data["creations"])
      markdown_resume = await create_resume(validate_user_data["profile"], creation["keywords"],  creation["job_description_lang"], template, pre_processing_rules, globalRules, request.lang, validate_user_data["currentPlan"])

      # Get the ATS score and tips
      currentStep = 4
      await updateProgress(validate_user_data["user_ref"], request.idDraft, current_function, currentStep, "ats_analysing", validate_user_data["creations"])
      ats_score_rules = manageTemplate.get("ats_completion",{})
      caculated_ats_score_json = await calculate_ats_score(markdown_resume, creation["keywords"], ats_score_rules, validate_user_data["currentPlan"])

      if(caculated_ats_score_json):
         currentStep = 5
         await updateProgress(validate_user_data["user_ref"], request.idDraft, current_function, currentStep, "ats_processing", validate_user_data["creations"])
         ats_score = process_ats_score(caculated_ats_score_json, creation["keywords"])
         if(not ats_score):
            await compensate_credits(user_id, current_function)
            await updateProgress(validate_user_data["user_ref"], request.idDraft, current_function, currentStep, "ats_processing_error", validate_user_data["creations"])
            await setChatGptError("ats_not_processed", str(ats_score), user_id)
            return
         # Add the resume and matched keywords
         currentStep = 6
         await update_creation(validate_user_data["user_ref"], markdown_resume, caculated_ats_score_json, ats_score["ats"], ats_score["keywords"], validate_user_data["creations"], request.idDraft)
         await updateProgress(validate_user_data["user_ref"], request.idDraft, current_function, currentStep, "created", validate_user_data["creations"])
      else:
         await compensate_credits(user_id, current_function)
         await updateProgress(validate_user_data["user_ref"], request.idDraft, current_function, currentStep, "ats_analysing_error", validate_user_data["creations"])
         await setChatGptError("incorrect_json", str(caculated_ats_score_json), user_id)
         return
   except:
      await compensate_credits(user_id, current_function)
      await updateProgress(validate_user_data["user_ref"], request.idDraft, current_function, currentStep, "error", validate_user_data["creations"])

async def updateProgress(user_ref, document_id, type: str, currentStep:int, status: str, document:dict):
   if(type == "resume_creations"):
      try:
         success = True
         creation_index = next((i for i, c in enumerate(document) if c.get("id") == document_id), None)
         
         if creation_index is not None:
            # Update the specific creation's keywords
            document[creation_index]["status"] = status
            document[creation_index]["stepProgress"] = currentStep

            # Push the update to Firestore
            user_ref.update({"creations": document})
         else:
            success = False

         return {
            "success": success,
         }
      except Exception as e:
         raise HTTPException(status_code=501, detail=str(e))


async def updateViewed(user_ref, document_id, type: str, document:dict, viewed: bool):
   if(type == "resume_creations"):
      try:
         success = True
         creation_index = next((i for i, c in enumerate(document) if c.get("id") == document_id), None)
         print(document[creation_index])
         if creation_index is not None:
            document[creation_index]["viewed"] = viewed

            # Push the update to Firestore
            user_ref.update({"creations": document})
         else:
            success = False

         print(success)
         return {
            "success": success,
         }
      except Exception as e:
         raise HTTPException(status_code=501, detail=str(e))

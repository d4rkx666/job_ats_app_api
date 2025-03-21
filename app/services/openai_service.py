from openai import OpenAI
from app.core.config import settings
from app.models.schemas import ResumeRequest
import json

client = OpenAI(api_key = settings.openai_api_key)

async def optimize_resume(resume_text: str, job_title, job_description, lang, plan) -> str:

      # VARIABLES
      role_system = ""
      role_user = f""
      continue_process = True

      # Lang
      match lang:
            case settings.app_lang_en:
                  role_system = "You are a helpful assistant that optimizes resumes for ATS. Always without exception return your responses in the following JSON format: [{'category': String, 'suggestions': String[]}]"
                  role_user = f"Analyze this resume: {resume_text}, and suggest improvements for this job description: {job_description}."
            case settings.app_lang_es:
                  role_system = "Eres un asistente útil que optimiza CV para pasar el ATS. Siempre sin excepción regresa tus respuestas con este formato JSON: [{'category': String, 'suggestions': String[]}]"
                  role_user = f"Analiza este CV: {resume_text}, y sugiere mejoras para esta descripción de trabajo: {job_description}."
            case _:
                  continue_process = False

      # Call OpenAI API
      if(continue_process):
            model_gpt = settings.app_free_model
            match plan:
                  case "free":
                        model_gpt = settings.app_free_model
                  case "pro":
                        model_gpt = settings.app_pro_model
                  case "business":
                        model_gpt = settings.app_business_model
                  case _:
                        model_gpt = settings.app_free_model



            completion = client.chat.completions.create(
            model=model_gpt,
            messages=[
                  {"role": "system", "content": role_system},
                  {"role": "user", "content": role_user}
            ],
                  max_tokens=500
            )
            
            # Get the response and print it
            model_response = completion.choices[0].message.content

            # Load the JSON string 
            data = json.loads(model_response)

            return {"optimized_resume": data}
      else:
            raise HTTPException(status_code=408, detail="Language not found.")

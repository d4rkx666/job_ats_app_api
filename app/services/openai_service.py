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
                  role_system = settings.app_ai_c1_role_system_en
                  role_user = f"{settings.app_ai_c1_role_user_en} resume:{resume_text} job description:{job_description}."
            case settings.app_lang_es:
                  role_system = settings.app_ai_c1_role_system_es
                  role_user = f"{settings.app_ai_c1_role_user_es} CV:{resume_text} puesto:{job_description}."
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

            return model_response
      else:
            return ""




async def create_resume(profile: str, name: str, email: str, linkedin: str, website: str, job_description: str, keywords: str, template: dict, rules: dict, lang: str, plan) -> str:

      # VARIABLES
      role_system = template["system"]
      role_user = f"{template["task"]} User profile:{name} {email} {linkedin} {website} {profile}. Job description:{job_description}. Keywords:{','.join(f'{kw}' for kw in keywords)}. Required sections:{', '.join(f'{kw}' for kw in rules["required_sections"])}, Rules:{','.join(f'{r}' for r in template["rules"])},{','.join(f'{r}' for r in rules["keyword_handling"])}. Strict response format: {rules["document_format"]["example"]}."
      continue_process = True
      current_lang = ""

      # Lang
      match lang:
            case settings.app_lang_en:
                  current_lang = "Response language: English"
            case settings.app_lang_es:
                  current_lang = "Response language: Spanish"
            case _:
                  continue_process = False

      role_user = f"{role_user} {current_lang}"

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



            """completion = client.chat.completions.create(
            model=model_gpt,
            messages=[
                  {"role": "system", "content": role_system},
                  {"role": "user", "content": role_user}
            ],
                  max_tokens=500
            )
            
            # Get the response and print it
            model_response = completion.choices[0].message.content"""

            model_response = """{
  "resume": "---\n# **Felix Abraham Catzin Huh**  \n`themasterdarkness219@gmail.com`  \n\n---\n### **Professional Summary**  \nJava Full Stack Developer with 3+ years of experience in ==Spring==, ==AWS==, and ==REST APIs==. Strong expertise in problem-solving and multilingual (English/Spanish).  \n\n---\n## **Experience**  \n**==Especialista de Java==** @ Telcel *(Sep 2020 - Jan 2024)*  \n- Developed backend systems using ==Java EE==, ==Apache Camel==, and ==PostgreSQL==.  \n- Automated tasks via ==UNIX/Linux scripting== and deployed solutions on ==Cloud (AWS)==.  \n\n---\n## **Education**  \n**Ingenier\\u00eda en Tecnolog\\u00edas de la Informaci\\u00f3n**  \n*Universidad Tecnol\\u00f3gica de Canc\\u00fan* | 2014 - 2018  \n\n---\n## **Skills**  \n`Java` `Spring` `AWS` `PostgreSQL`  \n`Apache Camel` `REST APIs` `Groovy`  \n`IntelliJ/Eclipse` `UNIX/Linux`  \n`English & Spanish (Fluent)`  \n\n---\n*Format: Skills aligned right in 2-column layout. Keywords highlighted per prompt rules.*",
  "tips": [
    "For ATS, ensure keywords match the job description (e.g., 'Apache Camel' vs 'Cron Jobs').",
    "Use bullet points for readability; avoid paragraphs longer than 2 lines.",
    "If adding Projects, focus on quantifiable outcomes (e.g., 'Optimized API response time by 30%')."
  ],
  "ats_score": 80
}"""
            return model_response
      else:
            return ""
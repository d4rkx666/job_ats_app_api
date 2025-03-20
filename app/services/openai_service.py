from openai import OpenAI
from app.core.config import settings
from app.models.schemas import ResumeRequest
import json

client = OpenAI(api_key = settings.openai_api_key)

async def optimize_resume(resume_text: str, job_title, job_description, lang) -> str:

      # VARIABLES
      role_system = ""
      role_user = f""
      continue_process = True

      # Lang
      match lang:
            case settings.app_lang_en:
                  role_system = "You are a helpful assistant that optimizes resumes for ATS. Always return your responses in the following JSON format: [{'category': String, 'suggestions': String[]}]"
                  role_user = f"Analyze this resume: {resume_text}, and suggest improvements for this job description: {job_description}."
            case settings.app_lang_es:
                  role_system = "Eres un asistente útil que optimiza curriculums para pasar el ATS. Siempre regresa tus respuestas con este formato JSON: [{'category': String, 'suggestions': String[]}]"
                  role_user = f"Analiza este curriculum: {resume_text}, y sugiere mejoras para esta descripción de trabajo: {job_description}."
            case _:
                  continue_process = False

      # Call OpenAI API
      if(continue_process):
            """response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                  {"role": "system", "content": role_system},
                  {"role": "user", "content": role_user}
            ],
            max_tokens=300
            )"""
            
            temp_response = """[
                  {
                  "category": "Profile Summary",
                  "suggestions": [
                        "Emphasize expertise in Java, Spring Boot, React.js, Python, and PHP.",
                        "Highlight experience with AWS, WebSphere, Docker, and DevOps tools.",
                        "Mention ability to work in Agile/Scrum environments and UI/UX design skills."
                  ]
                  },
                  {
                  "category": "Work Experience",
                  "suggestions": [
                        "Quantify achievements, such as 'improving response time by 80%' in API development.",
                        "Emphasize security enhancements using Java Spring Security.",
                        "Highlight cloud migration and automation experience."
                  ]
                  },
                  {
                  "category": "ATS Optimization",
                  "suggestions": [
                        "Ensure keywords like 'RESTful APIs,' 'microservices,' and 'SQL' are included.",
                        "Use terms that match job descriptions, such as 'cloud deployment' and 'CI/CD pipelines.'"
                  ]
                  },
                  {
                  "category": "UI/UX Integration",
                  "suggestions": [
                        "Connect UI/UX knowledge with front-end development skills.",
                        "Mention Figma wireframing and usability testing experience."
                  ]
                  },
                  {
                  "category": "Resume Formatting",
                  "suggestions": [
                        "Keep the resume within two pages for better readability.",
                        "Use a clear structure with bold section headers and bullet points.",
                        "Ensure a balance between technical and soft skills."
                  ]
                  }
                  ]
                  """
            # Load the JSON string 
            data = json.loads(temp_response)

            # Dump the dictionary back to a JSON string without spaces
            cleaned_tmp_response = json.dumps(data, separators=(',', ':'))

            return {"optimized_resume": cleaned_tmp_response}
      else:
            raise HTTPException(status_code=408, detail="Language not found.")

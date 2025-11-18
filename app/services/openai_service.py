from openai import OpenAI
import json
from app.core.config import settings
from app.utils.text import clean_text
from app.services.chat_gpt_schema.api_schema import extract_keywords_schema, ats_score_schema, optimize_resume_schema

client = OpenAI(api_key = settings.openai_api_key)

async def optimize_resume(resume_text: str, job_title: str, job_description: str, rules: dict, plan) -> str:

   # VARIABLES
   role_system = f"{rules["system"]}"
   role_user = f"""Job title: {job_title}

   Job Description: {job_description}

   Resume: {resume_text}"""
   continue_process = True

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
            {"role": "user", "content": role_user}],
         max_prompt_tokens=6000,
         tools=optimize_resume_schema(rules),
         tool_choice={"type": "function", "function": {"name": "optimize_resume"}},
      )
      
      # Get the response and print it
      model_response = completion.choices[0].message.tool_calls
      json_response = {}
      if model_response:
         json_response = json.loads(
            model_response[0].function.arguments
         )

      print("optimization:")
      print(json_response)

      return json_response
   else:
      return ""


async def extract_keywords_ai(job_description, rules: dict, plan) -> dict:

   # VARIABLES
   role_system = f"{rules["system"]}"
   role_user = f"Job description: [{job_description}]"
   continue_process = True

   # Call OpenAI API
   if(continue_process):
      model_gpt = settings.app_free_model
      match plan:
         case "free":
            model_gpt = settings.app_free_model
         case "pro":
            model_gpt = settings.app_free_model
         case "business":
            model_gpt = settings.app_business_model
         case _:
            model_gpt = settings.app_free_model

      #print(role_system+"\n\n"+role_user)
      completion = client.chat.completions.create(
      model=model_gpt,
      messages=[
         {"role": "system", "content": role_system},
         {"role": "user", "content": role_user}],
      max_prompt_tokens=6000,
      tools=extract_keywords_schema(rules),
      tool_choice={"type": "function", "function": {"name": "extract_keywords"}},
      )

      model_response = completion.choices[0].message.tool_calls
      json_response = {}
      if model_response:
         json_response = json.loads(
            model_response[0].function.arguments
         )

      print("extracted kws:")
      print(json_response)
      return json_response
   else:
      return {}
      

async def create_resume(profile: dict, keywords: dict, job_description_lang: str, template: dict, pre_processing_rules: dict, global_rules: dict, lang: str, plan) -> str:
   
   continue_process = True

   # First PRE PROCESS THE RESUME
   json_processed_resume= await pre_process_resume(profile, keywords, pre_processing_rules, job_description_lang, plan)

   # VARIABLES
   role_system = f"""{template["system"]}.
   STRICT RESPONSE RULES:
   {'\n'.join(f'   - {r}' for r in global_rules["document_format"]["formats"])}."""

   role_user = f"""{template["task"]}.
   RULES:
   {'\n'.join(f'   - {r}' for r in template["rules"])}.
   
   Here is the JSON resume: {clean_text(json_processed_resume)}"""
   

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


      #print("create: \n"+role_system+"\n\n"+role_user)
      completion = client.chat.completions.create(
      model=model_gpt,
      messages=[
         {"role": "system", "content": role_system},
         {"role": "user", "content": role_user}
      ],
         max_prompt_tokens=6000,
      )
      
      # Get the response and print it
      model_response = completion.choices[0].message.content
      
      print("create resume: ")
      print(model_response)
      return model_response
   else:
      return ""
   
async def pre_process_resume(profile: dict, keywords: dict, rules: dict, job_description_lang:str, plan) -> str:

   # VARIABLES
   role_system = f"""{rules["system"]}
   
   STRICT OUTPUT RULES:
   - Language in {job_description_lang}
   - Output a VALID JSON string without break lines nor extra spaces"""

   role_user = f"""{rules["task"]}.

   RULES:
   {'\n'.join(f'  - {r}' for r in rules["rules"])}
   
   Job description keywords: {','.join(f"{r["keyword"]}" for r in keywords)}

   Here's the JSON profile data: {str(profile)}"""
   continue_process = True

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


      #print("preprocess: \n"+role_system+"\n\n"+role_user)
      completion = client.chat.completions.create(
         model=model_gpt,
         messages=[
            {"role": "system", "content": role_system},
            {"role": "user", "content": role_user}],
         max_prompt_tokens=6000,
      )
      
      # Get the response and print it
      model_response = completion.choices[0].message.content

      print("pre process model: ")
      print(model_response)
      return model_response
   else:
      return ""



async def calculate_ats_score(markdown_resume: str, keywords: dict, rules: dict, plan) -> dict:

   # VARIABLES
   role_system = f"{rules["system"]}"

   role_user = f"""Job Description Keywords: {','.join(f"{r["keyword"]}" for r in keywords)}
   Resume in Markdown: {markdown_resume}"""
   continue_process = True

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
         {"role": "user", "content": role_user}],
      max_prompt_tokens=6000,
      tools=ats_score_schema(rules),
      tool_choice={"type": "function", "function": {"name": "ats_score"}},
      )

      # Extract the JSON arguments from the function call
      model_response = completion.choices[0].message.tool_calls
      json_response = {}
      if model_response:
         json_response = json.loads(
            model_response[0].function.arguments
         )
      
      print("ats score: ")
      print(model_response[0].function.arguments)
      return json_response
   else:
      return ""
   


async def recalculate_ats_score(markdown_resume: str, prev_analysis: str, keywords: dict, rules: dict, plan) -> dict:

   # VARIABLES
   role_system = f"""{rules["system"]}.
   *IMPORTANT RULE*
      - ONLY ANALYZE BASED ON YOUR PREVIOUS ANALYSIS
      - ADD KEYWORDS MATCHED IN THE RESUME INTO YOUR ANALYSIS
      
   PREVIOUS ANALYSIS: {prev_analysis}"""

   role_user = f"""Job Description Keywords: {','.join(f"{r["keyword"]}" for r in keywords)}
   Resume in Markdown: {markdown_resume}"""
   continue_process = True

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
         {"role": "user", "content": role_user}],
      max_prompt_tokens=6000,
      tools=ats_score_schema(rules),
      tool_choice={"type": "function", "function": {"name": "ats_score"}},
      )

      # Extract the JSON arguments from the function call
      model_response = completion.choices[0].message.tool_calls
      json_response = {}
      if model_response:
         json_response = json.loads(
            model_response[0].function.arguments
         )
      
      print("ats score: ")
      print(model_response[0].function.arguments)
      return json_response
   else:
      return ""
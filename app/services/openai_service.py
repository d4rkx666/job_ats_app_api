from openai import OpenAI
from app.core.config import settings

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
         role_user = f"{settings.app_ai_c1_role_user_en} resume:{resume_text} job:{job_title} {job_description}."
      case settings.app_lang_es:
         role_system = settings.app_ai_c1_role_system_es
         role_user = f"{settings.app_ai_c1_role_user_es} CV:{resume_text} puesto:{job_title} {job_description}."
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
         max_tokens=800
      )
      
      # Get the response and print it
      model_response = completion.choices[0].message.content

      return model_response
   else:
      return ""


async def extract_keywords_ai(job_description, rules: dict, plan) -> str:

   # VARIABLES
   role_system = f"{rules["system"]}. STRICT RESPONSE RULES:{','.join(f'{r}' for r in rules["global_rules"]["formats"])}. Example: {rules["global_rules"]["example"]}"
   role_user = f"{rules["user"]} [{job_description}]"
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

      #print(role_system+"\n\n"+role_user)
      completion = client.chat.completions.create(
      model=model_gpt,
      messages=[
         {"role": "system", "content": role_system},
         {"role": "user", "content": role_user}
      ],
         max_tokens=1000,
         temperature= 0.3,
      )
      
      # Get the response and print it
      model_response = completion.choices[0].message.content
      #model_response="""{"keywords":[{"keyword":"Java","type":"hard skill","count":2},{"keyword":"Java 8","type":"hard skill","count":1},{"keyword":"Streams","type":"hard skill","count":1},{"keyword":"Lambdas","type":"hard skill","count":1},{"keyword":"Spring","type":"tool","count":1},{"keyword":"Inversion del Control (IoC)","type":"soft skill","count":1},{"keyword":"Inyeccion de dependencias (ID)","type":"soft skill","count":1},{"keyword":"Anotaciones y Estereotipos","type":"soft skill","count":1},{"keyword":"Data Web","type":"tool","count":1},{"keyword":"Lombok","type":"tool","count":1},{"keyword":"Rest Template","type":"tool","count":1},{"keyword":"Web Client","type":"tool","count":1},{"keyword":"Security","type":"soft skill","count":1},{"keyword":"SWAGGER","type":"tool","count":1},{"keyword":"ASYNC API","type":"tool","count":1},{"keyword":"Unite Test","type":"tool","count":1},{"keyword":"Junit","type":"tool","count":1},{"keyword":"Mokito","type":"tool","count":1},{"keyword":"Versionamiento e integracion continua","type":"soft skill","count":1},{"keyword":"CI | CD","type":"tool","count":1},{"keyword":"Maven","type":"tool","count":1},{"keyword":"Manejo de Git","type":"tool","count":1},{"keyword":"Jenkins","type":"tool","count":1},{"keyword":"Sonar","type":"tool","count":1},{"keyword":"Black Duck","type":"tool","count":1},{"keyword":"Veracode","type":"tool","count":1},{"keyword":"Fortify","type":"tool","count":1},{"keyword":"Nexus","type":"tool","count":1},{"keyword":"GIT Actions","type":"tool","count":1},{"keyword":"Jfrog","type":"tool","count":1},{"keyword":"Containerizacion","type":"soft skill","count":1},{"keyword":"Kubernetes","type":"tool","count":1},{"keyword":"OpenShift","type":"tool","count":1},{"keyword":"Secrets | ConfigMap","type":"tool","count":1},{"keyword":"Docker","type":"tool","count":1},{"keyword":"Patrones de Diseño","type":"soft skill","count":1},{"keyword":"Singleton","type":"soft skill","count":1},{"keyword":"Builder","type":"soft skill","count":1},{"keyword":"SOLID","type":"soft skill","count":1},{"keyword":"Microservicios","type":"soft skill","count":1},{"keyword":"Protocolo HTTP (conceptos, verbos)","type":"soft skill","count":1},{"keyword":"HHTP Metods","type":"soft skill","count":1},{"keyword":"TLS Verbs","type":"soft skill","count":1},{"keyword":"DB","type":"soft skill","count":1},{"keyword":"MySQL","type":"tool","count":1},{"keyword":"Posgress","type":"tool","count":1},{"keyword":"SQLServer","type":"tool","count":1},{"keyword":"Mongo DB","type":"tool","count":1},{"keyword":"Redis","type":"tool","count":1},{"keyword":"Herramientas Agile","type":"soft skill","count":1},{"keyword":"Jira","type":"tool","count":1},{"keyword":"Confluence","type":"tool","count":1},{"keyword":"Metodologias","type":"soft skill","count":1},{"keyword":"Scrum","type":"soft skill","count":1},{"keyword":"Kamban","type":"soft skill","count":1},{"keyword":"Waterfall","type":"soft skill","count":1}]}"""
      print(model_response)
      return model_response
   else:
      return ""
      

async def create_resume(profile: dict, keywords: dict, template: dict, pre_processing_rules: dict, global_rules: dict, lang: str, plan) -> dict:

   # First PRE PROCESS THE RESUME
   pre_processed_resume = await pre_process_resume(profile, keywords, pre_processing_rules, plan)

   # VARIABLES
   role_system = f"{template["system"]}. STRICT RESPONSE RULES:{','.join(f'{r}' for r in global_rules["document_format"]["formats"])}."
   role_user = f"{template["task"]}. Rules:{','.join(f'{r}' for r in template["rules"])}. Here is the resume:{pre_processed_resume}."
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


      #print("create: \n"+role_system+"\n\n"+role_user)
      completion = client.chat.completions.create(
      model=model_gpt,
      messages=[
         {"role": "system", "content": role_system},
         {"role": "user", "content": role_user}
      ],
         max_tokens=1000,
      )
      
      # Get the response and print it
      model_response = completion.choices[0].message.content

      """model_response = {
         "resume": "# Felix Abraham Catzin Huh\\nfcatzin@hotmail.com\\n\\n## Professional Summary\\nDesarrollador Java con experiencia en diseño de APIs escalables y mantenimiento de sistemas robustos. Experto en optimización de código, arquitectura de microservicios y manejo de bases de datos. Contribuye a proyectos de alto impacto con un enfoque ágil y enfoque en la eficiencia operativa.\\n\\n## Skills\\n- **Java**\\n- **Spring Boot**\\n- Microservicios\\n- **API**\\n- **Oracle DB**\\n- **Jira**\\n- Scrum\\n- **CI/CD**\\n- Jenkins\\n- SonarQube\\n- **Android Studio**\\n- **GIT**\\n- **SVN**\\n- **Websphere**\\n\\n## Experience\\n### **Especialista de Java** - Telcel (9/2020 - 1/2024)\\n- Desarrollo y mantenimiento de API escalable para aplicación de firma de contratos.\\n- Uso de Java Spring Boot para arquitectura de microservicios, mejorando la eficiencia de los servicios móviles.\\n- Optimización de código, mejorando tiempos de respuesta en un 80%.\\n- Participación en equipos ágiles (Scrum y Kanban) y colaboración en equipo DevOps.\\n- Desarrollo del módulo de seguridad en aplicación móvil con **Android Studio**.\\n- Migración de sistemas de Java 8 a Java 12, reduciendo costos de mantenimiento.\\n- Implementación de **CI/CD** con Jenkins y pruebas automatizadas con SonarQube.\\n- Configuración de JNDI en Websphere.\\n- Control de versiones con **GIT** y **SVN**.\\n\\n## Education\\n### Ingeniería en Tecnologías de la Información y Comunicación\\nUniversidad Tecnológica de Cancún (9/2014 - 8/2018)\\n\\n## Projects (Optional)\\n- **Proyecto de Firma Digital**: Desarrollo de una API escalable con **Java** para la firma digital de contratos en una plataforma móvil.\\n- **Migración a Java 12**: Proyecto de migración de sistemas de Java 8 a Java 12, con beneficios en flexibilidad y costos.\\n\\n",
         "tips": [
         "Utiliza palabras clave en las secciones de experiencia y habilidades para mejorar la visibilidad en sistemas ATS.",
         "Usa negritas para resaltar títulos de puestos y habilidades clave.",
         "Mantén las descripciones concisas para una lectura rápida y eficaz.",
         "Divide sutilmente las secciones para mantener el diseño limpio y organizado."
         ],
         "ats_score": 90
         }"""
      
      print("create resume: ")
      print(model_response)
      return {"processed_resume":pre_processed_resume, "markdown_resume": model_response}
   else:
      return ""
   
async def pre_process_resume(profile: dict, keywords: dict, rules: dict, plan) -> str:

   # VARIABLES
   role_system = f"{rules["system"]}. STRICT RESPONSE RULES:{','.join(f'{r}' for r in rules["document_format"]["formats"])}"
   role_user = f"{rules["task"]} {','.join(f'{r}' for r in rules["rules"])}. Here are the JD keywords:[{','.join(f"{r["keyword"]}" for r in keywords)}] Here's the profile data:{str(profile)}"
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
         {"role": "user", "content": role_user}
      ],
         max_tokens=1000,
      )
      
      # Get the response and print it
      model_response = completion.choices[0].message.content

      #model_response = """{"something":"asdasd"}"""

      print("pre process model: ")
      print(model_response)
      return model_response
   else:
      return ""



async def calculate_ats_score(markdown_resume: str, keywords: dict, rules: dict, plan) -> str:

   # VARIABLES
   role_system = f"{rules["system"]}. STRICT RESPONSE RULES:{','.join(f'{r}' for r in rules["document_format"]["formats"])}. Output example: {rules["document_format"]["example"]}"
   role_user = f"{rules["task"]}: {','.join(f'{r}' for r in rules["rules"])}. Here are the JD keywords:[{','.join(f"{r["keyword"]}" for r in keywords)}] Here's the resume in markdown format:[{markdown_resume}]"
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


      #print("calculate ats: \n"+role_system+"\n\n"+role_user+"\n\n")
      completion = client.chat.completions.create(
      model=model_gpt,
      messages=[
         {"role": "system", "content": role_system},
         {"role": "user", "content": role_user}
      ],
         max_tokens=1000,
      )
      
      # Get the response and print it
      model_response = completion.choices[0].message.content

      #model_response = """{"something":"asdasd"}"""
      
      print("ats score: ")
      print(model_response)
      return model_response
   else:
      return ""
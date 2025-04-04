from fastapi import HTTPException
from app.services.firebase_service import db


async def get_templates():
   try:
      template_db = db.collection("templates").document("template")
      template = template_db.get().to_dict()

      return template
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
   
async def get_global_rules():
   try:
      rules_db = db.collection("templates").document("global_rules")
      rules = rules_db.get().to_dict()

      return rules
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
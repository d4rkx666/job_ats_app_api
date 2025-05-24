from fastapi import APIRouter, Request, HTTPException
from app.services.user_actions_manager import reset_monthly_credits_and_plans
from app.core.config import settings


router = APIRouter()

@router.post("/daily-reset")
async def daily_reset(request: Request):
   try:
      auth = request.headers.get('authorization').split(" ")[1]
      if(not auth or auth != settings.cron_secret):
         raise HTTPException(status_code=401, detail="Not authorized")
      
      # Reset credits
      reset_monthly_credits_and_plans()
      return {"success":True}
   except Exception as e:
      print(e)
      raise HTTPException(status_code=401, detail="Not authorized")

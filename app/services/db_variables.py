from fastapi import HTTPException
from app.services.firebase_service import db


async def get_costs():
   try:
      cost_db = db.collection("global_variables").document("action_cost")
      cost = cost_db.get().to_dict()

      return cost
   except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))
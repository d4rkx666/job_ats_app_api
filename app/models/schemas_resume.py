from pydantic import BaseModel

class ResumeBackgroundTasksResponse(BaseModel):
   success: bool
   message: str
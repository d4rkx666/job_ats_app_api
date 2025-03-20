from pydantic import BaseModel
from fastapi import UploadFile, File, Form
from datetime import datetime


## REQUESTS 
class InsertDataRequest(BaseModel):
   name: str
   country: str
   email: str
   password: str

class ResumeRequest(BaseModel):
   resume_file: UploadFile = File(...)
   job_description: str = Form(...)

class FeedbackRequest(BaseModel):
   stars: int
   comment: str


## RESPONSES
class OptimizedResumeResponse(BaseModel):
   optimized_resume: str

from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core import PydanticCustomError
from typing import Optional
from fastapi import UploadFile, File, Form
from bleach import clean
import re

## SUB REQUESTS

class DateManage(BaseModel):
   month: Optional[int]
   year: Optional[int]

class ProfileEducationSubRequest(BaseModel):
   degree: str
   institution: str
   graduationStartDate: DateManage
   graduationEndDate: DateManage

   @field_validator("degree", "institution")
   @classmethod
   def sanitize_strings(cls, v: str | None) -> str | None:
      if not v:
         return v
      return clean(v)  # Strips HTML/JS tags

class ProfileJobSubRequest(BaseModel):
   title: str
   company: str
   startDate: DateManage
   endDate: DateManage
   responsibilities: str

   @field_validator("title", "company", "responsibilities")
   @classmethod
   def sanitize_strings(cls, v: str | None) -> str | None:
      if not v:
         return v
      return clean(v)  # Strips HTML/JS tags

class ProfileProjectSubRequest(BaseModel):
   name: str
   description: str
   technologies: str

   @field_validator("name", "description", "technologies")
   @classmethod
   def sanitize_strings(cls, v: str | None) -> str | None:
      if not v:
         return v
      return clean(v)  # Strips HTML/JS tags


## REQUESTS 
class InsertDataRequest(BaseModel):
   name: str
   country: str
   email: EmailStr
   password: str

   @field_validator("name", "country", "email", "password")
   @classmethod
   def sanitize_strings(cls, v: str | None) -> str | None:
      if not v:
         return v
      return clean(v)  # Strips HTML/JS tags

class ResumeRequest(BaseModel):
   resume_file: UploadFile = File(...)
   job_description: str = Form(...)

   ## SANITAZING FIELDS FROM FRONT END
   @field_validator("job_description")
   @classmethod
   def sanitize_strings(cls, v: str | None) -> str | None:
      if not v:
         return v
      return clean(v)  # Strips HTML/JS tags

class FeedbackRequest(BaseModel):
   stars: int
   comment: str

   ## SANITAZING FIELDS FROM FRONT END
   @field_validator("comment")
   @classmethod
   def sanitize_strings(cls, v: str | None) -> str | None:
      if not v:
         return v
      return clean(v)  # Strips HTML/JS tags

class ProfilePersonalInformationRequest(BaseModel):
   email: EmailStr
   phone: str
   linkedin: str
   website: str

   ## SANITAZING FIELDS FROM FRONT END
   @field_validator("website", "linkedin")
   @classmethod
   def sanitize_strings(cls, v: str | None) -> str | None:
      if not v:
         return v
      return clean(v)  # Strips HTML/JS tags

   # Custom validation for 'website' format
   @field_validator("website", "linkedin")
   @classmethod
   def validate_url(cls, v: str | None) -> str | None:
      if v and not v.startswith(("http://", "https://")):
         raise PydanticCustomError(
               "invalid_url",
               "URL must start with http:// or https://"
         )
      return v

   @field_validator("phone")
   @classmethod
   def validate_and_sanitize_phone(cls, v: str) -> str:
      # Step 1: Sanitize (remove HTML/JS tags)
      sanitized = clean(v.strip())

      # Step 2: Remove non-numeric characters (except optional leading '+')
      numeric_only = re.sub(r"[^\d+]", "", sanitized)
      if not numeric_only:
         raise PydanticCustomError(
               "invalid_phone",
               "Phone number must contain at least 10 digits"
         )

      # Step 3: Validate length (adjust as needed)
      min_digits = 10  # Minimum digits (excluding '+')
      digits = numeric_only.lstrip("+")  # Ignore leading '+' for counting
      if len(digits) < min_digits:
         raise PydanticCustomError(
               "invalid_phone",
               f"Phone number must have at least {min_digits} digits"
         )

      return numeric_only  # Return sanitized + validated phone
   
class ProfileSkillsRequest(BaseModel):
   skills: list[str]
   

class ProfileRequest(BaseModel):
   educations: list[ProfileEducationSubRequest]
   jobs: list[ProfileJobSubRequest]
   projects: list[ProfileProjectSubRequest]

class KeywordOptimizationRequest(BaseModel):
   job_title: str
   job_description: str
   type: str = None
   lang: str
   isDraft: bool
   idDraft: Optional[str] = None

   @field_validator("job_title", "job_description", "type", "lang")
   @classmethod
   def sanitize_strings(cls, v: str | None) -> str | None:
      if not v:
         return v
      return clean(v)  # Strips HTML/JS tags




## RESPONSES
class OptimizedResumeResponse(BaseModel):
   optimized_resume: str
   success: bool
   type_error: str

   
class OptimizedKeywordsResponse(BaseModel):
   keywords: list[str]
   score: int
   success: bool
   type_error: str
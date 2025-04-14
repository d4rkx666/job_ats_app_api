from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from app.core.security import get_current_user
from app.models.schemas import ExportPDFRequest, ExportDOCXRequest
from app.core.config import settings
from app.services.user_actions_manager import getUserData
import pdfkit
import base64
import os
from htmldocx import HtmlToDocx
from docx import Document
from tempfile import NamedTemporaryFile
import io

router = APIRouter()

@router.post("/export-pdf")
async def export_pdf(request: ExportPDFRequest ,user: dict = Depends(get_current_user)):

   # Configure default PDF options
   default_options = {
      'page-size': 'A4',
      'margin-top': '0.5in',
      'margin-right': '0.5in',
      'margin-bottom': '0.5in',
      'margin-left': '0.5in',
      'encoding': 'UTF-8',
      'quiet': '',
      'enable-local-file-access': None,  # Required for wkhtmltopdf >= 0.12.6
      'no-outline': None,
      'disable-smart-shrinking': None,
      'print-media-type': None,
      'dpi': 300,
      'zoom': 1.0,
      'user-style-sheet': os.path.join(os.path.dirname(__file__), 'styles.css'),
   }
   
   try:
      # Create a temporary HTML file to ensure all assets are properly handled
      with NamedTemporaryFile(suffix='.html', delete=False, mode='w+', encoding='utf-8') as html_file:
         html_file.write(request.html)
         html_file_path = html_file.name
      
      # Configure pdfkit path (adjust based on your server setup)
      config = pdfkit.configuration(wkhtmltopdf=settings.wkhtmltopdf_path)
      
      # Generate PDF
      pdf_bytes = pdfkit.from_file(
         html_file_path,
         False,  # Don't output to file
         options=default_options,
         configuration=config
      )
      
      # Clean up temporary file
      try:
         os.unlink(html_file_path)
      except:
         pass
      
      return {
         "success": True,
         "pdf": base64.b64encode(pdf_bytes).decode('utf-8'),
         "type_error": ""
      }

   except Exception as e:
      # Clean up temporary file if it exists
      if 'html_file_path' in locals():
         try:
               os.unlink(html_file_path)
         except:
               pass
      raise HTTPException(status_code=500, detail=str(e))

   except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
   

@router.post("/export-docx")
async def export_docx(request: ExportDOCXRequest ,user: dict = Depends(get_current_user)):

   try:

      # Get user data
      validate_user_data = await getUserData(user["uid"])

      if(validate_user_data["currentPlan"] == "pro"):
         
         # Initialize parser
         new_parser = HtmlToDocx()
         
         # Create empty document
         doc = Document()
         
         # Parse HTML (preserves styles, tables, lists)
         new_parser.add_html_to_document(request.html, doc)
         
         # 3. Save to in-memory file
         file_stream = io.BytesIO()
         doc.save(file_stream)
         file_stream.seek(0)  # Critical!
         
         # 4. Return binary response
         return Response(
            content=file_stream.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                  "Content-Disposition": "attachment; filename=resume.docx",
                  "Content-Length": str(len(file_stream.getvalue()))
            }
         )
   
      else:
          return{
              "error": True,
              "type": "user_not_pro_plan"
          }
      
   except Exception as e:
      print(f"DOCX generation failed: {str(e)}")  # Server-side logging
      raise HTTPException(
         status_code=500,
         detail=f"DOCX generation failed: {str(e)}"
      )
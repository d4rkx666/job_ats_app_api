from fastapi import APIRouter, Depends, Response
from app.core.security import get_current_user
from app.models.schemas import ExportPDFRequest, ExportDOCXRequest
from app.services.user_actions_manager import getUserData
import base64
from htmldocx import HtmlToDocx
from docx import Document
import io
from io import BytesIO
from xhtml2pdf import pisa


router = APIRouter()

@router.post("/export-pdf")
async def export_pdf(request: ExportPDFRequest, user: dict = Depends(get_current_user)):
    response = {
        "success": True,
        "pdf": "",
        "type_error": ""
    }

    try:
        pdf_buffer = BytesIO()

        # Generate PDF with most basic settings
        pisa_status = pisa.CreatePDF(
            src=request.html,
            dest=pdf_buffer,
            encoding='UTF-8',
            # Remove all problematic parameters
        )

        if pisa_status.err:
            print(f"PDF error: {pisa_status.err}")
            response.update({"success": False, "type_error": "pdf_generation_failed"})
            return response

        pdf_bytes = pdf_buffer.getvalue()
        pdf_buffer.close()

        return {
            "success": True,
            "pdf": base64.b64encode(pdf_bytes).decode('utf-8'),
            "type_error": ""
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        response.update({"success": False, "type_error": "pdf_generation_failed"})
        return response


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
              "success": False,
              "type": "user_not_pro_plan"
          }
      
   except Exception as e:
      print(f"DOCX generation failed: {str(e)}")  # Server-side logging
      return{
         "success": False,
         "type": "docx_generation_failed"
      }
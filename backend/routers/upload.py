from fastapi import APIRouter, UploadFile, File, HTTPException
from services.text_extractor import extract_text_from_pdf
from services.llm_service import evaluate_document_with_ai
from services.detection import analyze_text_authenticity
from services.verifier import verify_document_claims

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 Megabytes

@router.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported currently.")
    
    # 1. Check File Size (Backend Validation)
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File is too large. Please upload a PDF under 5MB.")
    
    try:
        contents = await file.read()
        extracted_text = extract_text_from_pdf(contents)
        
        # Run Services
        ai_results = evaluate_document_with_ai(extracted_text)
        authenticity_results = analyze_text_authenticity(extracted_text)
        fact_check_results = verify_document_claims(extracted_text) 
        
        return {
            "filename": file.filename,
            "status": "success",
            "evaluation": ai_results,
            "authenticity": authenticity_results,
            "verification": fact_check_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
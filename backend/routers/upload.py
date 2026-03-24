from fastapi import APIRouter, UploadFile, File, HTTPException
from services.text_extractor import extract_text_from_pdf
from services.llm_service import evaluate_document_with_ai
from services.detection import analyze_text_authenticity
from services.verifier import verify_document_claims
from utils.config import get_max_file_size_mb

router = APIRouter()

MAX_FILE_SIZE_MB = get_max_file_size_mb()
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

@router.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported currently.")
    
    # 1. Check File Size (Backend Validation)
    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File is too large. Please upload a PDF under {MAX_FILE_SIZE_MB}MB.")
    
    try:
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"File is too large. Please upload a PDF under {MAX_FILE_SIZE_MB}MB.")

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
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from services.llm_service import evaluate_document_with_ai
from services.detection import analyze_text_authenticity
from services.verifier import verify_document_claims, verify_single_claim

router = APIRouter(prefix="/api", tags=["evaluation"])


class EvaluateTextRequest(BaseModel):
	text: str = Field(..., min_length=50, description="Raw report/document text")


class VerifyClaimsRequest(BaseModel):
	claims: list[str] = Field(..., min_length=1, max_length=15)
	search_context: str = Field(default="")


@router.post("/evaluate-text")
def evaluate_text(payload: EvaluateTextRequest):
	try:
		ai_results = evaluate_document_with_ai(payload.text)
		authenticity = analyze_text_authenticity(payload.text)
		verification = verify_document_claims(payload.text)
		return {
			"status": "success",
			"evaluation": ai_results,
			"authenticity": authenticity,
			"verification": verification,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.post("/verify-claims")
def verify_claims(payload: VerifyClaimsRequest):
	try:
		results = [verify_single_claim(claim, payload.search_context) for claim in payload.claims]
		return {
			"status": "success",
			"count": len(results),
			"results": results,
		}
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Claim verification failed: {str(e)}")

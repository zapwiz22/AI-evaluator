import os
import json
import google.generativeai as genai
from utils.config import get_gemini_api_key


MODEL_CANDIDATES = [
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-pro-latest",
]


def _build_model() -> genai.GenerativeModel:
    for name in MODEL_CANDIDATES:
        try:
            return genai.GenerativeModel(
                name,
                generation_config={"response_mime_type": "application/json"},
            )
        except Exception:
            continue
    return genai.GenerativeModel(
        MODEL_CANDIDATES[0],
        generation_config={"response_mime_type": "application/json"},
    )


def _fallback_claim_result(claim: str) -> dict:
    return {
        "claim": claim,
        "status": "Unverified",
        "reason": "Automated verification unavailable because the LLM request failed (missing/invalid key, quota limit, or API error)."
    }


def _normalize_status(value: str) -> str:
    val = (value or "").strip().lower()
    if val == "verified":
        return "Verified"
    if val == "contradicted":
        return "Contradicted"
    return "Unverified"


def verify_single_claim(claim: str, search_context: str = "") -> dict:
    api_key = get_gemini_api_key()
    if not api_key:
        return _fallback_claim_result(claim)

    genai.configure(api_key=api_key)
    model = _build_model()

    prompt = f"""
    Evaluate the factual claim using the available context.

    Claim: "{claim}"
    Search Context: "{search_context if search_context else 'No external web evidence was provided.'}"

    Return strict JSON:
    {{
      "status": "Verified" or "Contradicted" or "Unverified",
      "reason": "one short sentence"
    }}
    """

    try:
        response = model.generate_content(prompt)
        parsed = json.loads(response.text)
        return {
            "claim": claim,
            "status": _normalize_status(parsed.get("status", "Unverified")),
            "reason": parsed.get("reason", "Evaluation unclear.")
        }
    except Exception as e:
        print(f"Verify claim error: {e}")
        return _fallback_claim_result(claim)

def verify_document_claims(text: str) -> list:
    """Extracts claims from text, 'searches' the web, and verifies them."""
    api_key = get_gemini_api_key()
    if not api_key:
        return []

    genai.configure(api_key=api_key)
    
    model = _build_model()
    
    # 1. EXTRACTION: Get 3 verifiable claims
    extract_prompt = f"""
    Extract 3 highly specific, verifiable factual claims from this text.
    Return ONLY a JSON array of strings. 
    Example: ["The company revenue grew by 20% in 2023.", "Python was created in 1991."]
    
    Text: {text[:10000]}
    """
    
    try:
        response = model.generate_content(extract_prompt)
        claims = json.loads(response.text)
        # Ensure it's a list even if the LLM wraps it in a dict
        if isinstance(claims, dict):
            claims = claims.get(list(claims.keys())[0], [])
        claims = claims[:3] # Limit to 3 for performance
    except Exception as e:
        print(f"Extraction Error: {e}")
        return []

    # 2 & 3. SEARCH AND VERIFY
    verification_results = []
    
    for claim in claims:
        # SIMULATED SEARCH: Replace this block later with a real API call 
        # (e.g., requests.get(f"https://api.tavily.com/search?query={claim}"))
        simulated_search_context = f"According to online sources discussing '{claim}', the general consensus aligns with standard industry data, though exact internal metrics may not be publicly available."
        verification_results.append(verify_single_claim(claim, simulated_search_context))
            
    return verification_results
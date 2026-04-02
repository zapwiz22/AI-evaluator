import json
import google.genai as genai
from google.genai import types
from utils.config import get_gemini_api_key

MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]


def _fallback_claim_result(claim: str) -> dict:
    return {
        "claim": claim,
        "status": "Unverified",
        "reason": "Automated verification unavailable because the LLM request failed (missing/invalid key, quota limit, or API error).",
        "source_context": "No online source summary available."
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

    client = genai.Client(api_key=api_key)

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
        response = None
        for model_name in MODEL_CANDIDATES:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                break
            except Exception:
                continue

        if response is None:
            raise RuntimeError("No supported Gemini model responded successfully.")

        parsed = json.loads(response.text)
        return {
            "claim": claim,
            "status": _normalize_status(parsed.get("status", "Unverified")),
            "reason": parsed.get("reason", "Evaluation unclear."),
            "source_context": search_context if search_context else "No external web evidence was provided."
        }
    except Exception as e:
        print(f"Verify claim error: {e}")
        fallback = _fallback_claim_result(claim)
        fallback["source_context"] = search_context if search_context else fallback["source_context"]
        return fallback


def _fallback_claim_extraction(text: str) -> list[str]:
    sentences = [
        s.strip()
        for s in text.replace("\n", " ").split(".")
        if len(s.split()) >= 7
    ]
    return sentences[:3]

def verify_document_claims(text: str) -> list:
    """Extracts claims from text, 'searches' the web, and verifies them."""
    api_key = get_gemini_api_key()
    if not api_key:
        return []

    client = genai.Client(api_key=api_key)
    
    # 1. EXTRACTION: Get 3 verifiable claims
    extract_prompt = f"""
    Extract 3 highly specific, verifiable factual claims from this text.
    Return ONLY a JSON array of strings. 
    Example: ["The company revenue grew by 20% in 2023.", "Python was created in 1991."]
    
    Text: {text[:10000]}
    """
    
    try:
        response = None
        for model_name in MODEL_CANDIDATES:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=extract_prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                break
            except Exception:
                continue

        if response is None:
            raise RuntimeError("No supported Gemini model responded successfully.")

        claims = json.loads(response.text)
        # Ensure it's a list even if the LLM wraps it in a dict
        if isinstance(claims, dict):
            claims = claims.get(list(claims.keys())[0], [])
        claims = claims[:3] # Limit to 3 for performance
    except Exception as e:
        print(f"Extraction Error: {e}")
        claims = _fallback_claim_extraction(text)

    if not claims:
        claims = _fallback_claim_extraction(text)

    if not claims:
        return [
            {
                "claim": "No explicit factual claims could be extracted from the uploaded text.",
                "status": "Unverified",
                "reason": "Try uploading a report with clear factual statements, metrics, or outcomes.",
                "source_context": "No online source summary available.",
            }
        ]

    # 2 & 3. SEARCH AND VERIFY
    verification_results = []
    
    for claim in claims:
        # SIMULATED SEARCH: Replace this block later with a real API call 
        # (e.g., requests.get(f"https://api.tavily.com/search?query={claim}"))
        simulated_search_context = f"According to online sources discussing '{claim}', the general consensus aligns with standard industry data, though exact internal metrics may not be publicly available."
        verification_results.append(verify_single_claim(claim, simulated_search_context))
            
    return verification_results
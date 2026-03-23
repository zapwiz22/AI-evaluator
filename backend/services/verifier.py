import os
import json
import google.generativeai as genai

def verify_document_claims(text: str) -> list:
    """Extracts claims from text, 'searches' the web, and verifies them."""
    
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )
    
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
    
    verify_prompt_template = """
    Original Claim: "{claim}"
    Web Search Context: "{search_summary}"
    
    Based ONLY on the web search context, evaluate the claim.
    Return JSON strictly matching this schema:
    {{
        "status": "Verified" or "Contradicted" or "Unverified",
        "reason": "A 1-sentence explanation of why."
    }}
    """

    for claim in claims:
        # SIMULATED SEARCH: Replace this block later with a real API call 
        # (e.g., requests.get(f"https://api.tavily.com/search?query={claim}"))
        simulated_search_context = f"According to online sources discussing '{claim}', the general consensus aligns with standard industry data, though exact internal metrics may not be publicly available."
        
        try:
            verify_response = model.generate_content(
                verify_prompt_template.format(claim=claim, search_summary=simulated_search_context)
            )
            result = json.loads(verify_response.text)
            
            verification_results.append({
                "claim": claim,
                "status": result.get("status", "Unverified"),
                "reason": result.get("reason", "Evaluation unclear.")
            })
        except Exception as e:
            verification_results.append({
                "claim": claim,
                "status": "Error",
                "reason": "Failed to verify this specific claim."
            })
            
    return verification_results
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
    # Try modern model names first; accounts for account/version availability.
    for name in MODEL_CANDIDATES:
        try:
            return genai.GenerativeModel(
                name,
                generation_config={"response_mime_type": "application/json"},
            )
        except Exception:
            continue
    # Final fallback if all candidates fail to initialize
    return genai.GenerativeModel(
        MODEL_CANDIDATES[0],
        generation_config={"response_mime_type": "application/json"},
    )


def _safe_fallback(text: str) -> dict:
    snippet = " ".join(text.split())[:600]
    return {
        "summary": "Automated summary unavailable because the LLM request failed (missing/invalid key, quota limit, or API error). The extracted text is available for manual review.",
        "key_findings": [
            "Document text was extracted successfully.",
            "LLM-based enrichment was skipped due to missing key or API error.",
            "Use /api/verify-claims endpoint for independent claim checks."
        ],
        "table_data": {
            "columns": ["Field", "Value"],
            "rows": [["Preview", snippet if snippet else "No text extracted"]]
        },
        "mermaid_flowchart": "graph TD; A[Upload PDF] --> B[Extract Text]; B --> C[Generate Brief]; C --> D[Review Output];",
        "requires_verification": []
    }

def evaluate_document_with_ai(text: str) -> dict:
    """Sends extracted text to an LLM to get summary, table, and flowchart data."""
    api_key = get_gemini_api_key()
    if not api_key:
        return _safe_fallback(text)

    genai.configure(api_key=api_key)
    
    model = _build_model()
    
    prompt = f"""
    You are an expert AI Evaluator. Analyze the following document text.
    Extract the key information and return it strictly as a JSON object with the following schema:
    {{
        "summary": "A concise, 3-4 sentence brief of the entire document.",
        "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
        "table_data": {{
            "columns": ["Column Name 1", "Column Name 2", "Column Name 3"],
            "rows": [["cell1", "cell2", "cell3"], ["cell1", "cell2", "cell3"]]
        }},
        "mermaid_flowchart": "A valid Mermaid.js graph TD string representing the core process or logic flow found in the text. Do not include markdown formatting blocks (like ```mermaid), just the raw code.",
        "requires_verification": ["A testable claim from the text", "Another testable claim"]
    }}
    
    Document Text:
    {text[:15000]} # Limiting to 15k characters for safety in this example
    """
    
    try:
        response = model.generate_content(prompt)
        result_dict = json.loads(response.text)

        if "table_data" not in result_dict:
            result_dict["table_data"] = {
                "columns": ["Note", "Value"],
                "rows": [["LLM", "No table_data returned"]]
            }
        return result_dict
    except Exception as e:
        print(f"LLM Processing Error: {e}")
        return _safe_fallback(text)
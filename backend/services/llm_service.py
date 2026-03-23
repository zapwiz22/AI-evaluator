import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def evaluate_document_with_ai(text: str) -> dict:
    """Sends extracted text to the LLM to get a summary, tables, and flowchart data."""
    
    # We use gemini-1.5-flash as it is fast and supports JSON output
    model = genai.GenerativeModel(
        'gemini-1.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt = f"""
    You are an expert AI Evaluator. Analyze the following document text.
    Extract the key information and return it strictly as a JSON object with the following schema:
    {{
        "summary": "A concise, 3-4 sentence brief of the entire document.",
        "key_findings": ["Finding 1", "Finding 2", "Finding 3"],
        "mermaid_flowchart": "A valid Mermaid.js graph TD string representing the core process or logic flow found in the text. Do not include markdown formatting blocks (like ```mermaid), just the raw code.",
        "requires_verification": ["A testable claim from the text", "Another testable claim"]
    }}
    
    Document Text:
    {text[:15000]} # Limiting to 15k characters for safety in this example
    """
    
    try:
        response = model.generate_content(prompt)
        # Parse the JSON string returned by the LLM into a Python dictionary
        result_dict = json.loads(response.text)
        return result_dict
    except Exception as e:
        raise Exception(f"LLM Processing Error: {str(e)}")
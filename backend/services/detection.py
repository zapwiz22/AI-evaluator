import os
import requests
import random
from dotenv import load_dotenv
from utils.config import get_gptzero_api_key

load_dotenv()

def analyze_text_authenticity(text: str) -> dict:
    """
    Sends text to detection APIs to calculate AI usage and Plagiarism.
    Falls back to simulated data if API keys are missing.
    """
    api_key = get_gptzero_api_key()
    
    # 1. AI Detection (Using GPTZero as the example)
    ai_score = 0
    if api_key and api_key != "your_gptzero_key_here":
        try:
            url = "https://api.gptzero.me/v2/predict/text"
            headers = {
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
            payload = {"document": text}
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            # GPTZero returns a probability between 0 and 1. We convert to a percentage.
            ai_score = int(data['documents'][0]['completely_generated_prob'] * 100)
        except Exception as e:
            print(f"GPTZero API Error: {e}")
            ai_score = min(95, max(5, int(len(text.split()) * 0.08)))
    else:
        # Deterministic fallback estimate if no API key is provided
        ai_score = min(95, max(5, int(len(text.split()) * 0.08)))

    # 2. Plagiarism Detection (Simulated)
    # Most plagiarism APIs (Copyleaks, Originality) require paid credits. 
    # You would replicate the block above with their specific API endpoint.
    # Lightweight heuristic fallback: repeated lines increase score.
    lines = [line.strip().lower() for line in text.splitlines() if line.strip()]
    duplicate_ratio = 0
    if lines:
        duplicate_ratio = 1 - (len(set(lines)) / len(lines))
    plagiarism_score = min(70, int(duplicate_ratio * 100) + random.randint(0, 8))
    
    return {
        "ai_probability_percent": ai_score,
        "plagiarism_percent": plagiarism_score
    }
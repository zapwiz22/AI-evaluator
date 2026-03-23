import os
import requests
import random
from dotenv import load_dotenv

load_dotenv()

def analyze_text_authenticity(text: str) -> dict:
    """
    Sends text to detection APIs to calculate AI usage and Plagiarism.
    Falls back to simulated data if API keys are missing.
    """
    api_key = os.getenv("GPTZERO_API_KEY")
    
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
            ai_score = random.randint(10, 85) # Fallback simulation
    else:
        # Simulate a score if no API key is provided
        ai_score = random.randint(10, 85)

    # 2. Plagiarism Detection (Simulated)
    # Most plagiarism APIs (Copyleaks, Originality) require paid credits. 
    # You would replicate the block above with their specific API endpoint.
    plagiarism_score = random.randint(0, 15) # Simulated 0-15% plagiarism
    
    return {
        "ai_probability_percent": ai_score,
        "plagiarism_percent": plagiarism_score
    }
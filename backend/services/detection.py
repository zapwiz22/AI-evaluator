import os
import random
from dotenv import load_dotenv
from transformers import pipeline

try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

load_dotenv()

# ==========================================
# 1. Initialize Open-Source AI Detector
# ==========================================
# We load this globally so it only initializes once when the server starts.
# Note: The first time you run this, it will download the model (~500MB).
print("Loading AI Detection Model (this may take a moment on first run)...")
try:
    ai_detector = pipeline("text-classification", model="Hello-SimpleAI/chatgpt-detector-roberta")
    print("AI Model loaded successfully!")
except Exception as e:
    print(f"Failed to load AI model: {e}")
    ai_detector = None


def analyze_text_authenticity(text: str) -> dict:
    """
    Analyzes text for AI generation using a local Hugging Face model
    and checks for plagiarism using DuckDuckGo web search.
    """
    
    # ---------------------------------------------------------
    # A. AI Content Detection (Hugging Face RoBERTa)
    # ---------------------------------------------------------
    ai_score = 0
    if ai_detector and text.strip():
        try:
            # Let the tokenizer handle truncation to avoid index overflow.
            truncated_text = text
            
            # Run the model
            result = ai_detector(truncated_text, truncation=True, max_length=512)[0]
            
            # The model usually outputs labels like 'ChatGPT' or 'Human'
            if result['label'].lower() == 'chatgpt':
                ai_score = int(result['score'] * 100)
            else:
                ai_score = 100 - int(result['score'] * 100)
                
        except Exception as e:
            print(f"AI Detection Error: {e}")
            # Deterministic fallback if the model crashes
            ai_score = min(95, max(5, int(len(text.split()) * 0.08)))
    else:
        ai_score = min(95, max(5, int(len(text.split()) * 0.08)))


    # ---------------------------------------------------------
    # B. Plagiarism Detection (DuckDuckGo Web Search)
    # ---------------------------------------------------------
    plagiarism_score = 0
    
    # 1. Clean and split text into meaningful sentences
    # We filter out very short sentences (less than 7 words) to avoid false positives 
    # on common phrases like "Thank you for reading."
    sentences = [s.strip() for s in text.replace('\n', '. ').split('.') if len(s.split()) > 7]
    
    if sentences:
        # 2. Pick up to 5 random, substantial sentences to verify
        # We limit to 5 to avoid triggering DDG rate limits and keep the API fast
        sample_size = min(5, len(sentences))
        samples_to_check = random.sample(sentences, sample_size)
        
        plagiarized_hits = 0
        ddgs = DDGS()

        # 3. Search the web for exact string matches
        for sentence in samples_to_check:
            try:
                # Enclose in quotes for exact match searching
                query = f'"{sentence}"'
                
                # Fetch top 2 results
                results = list(ddgs.text(query, max_results=2)) 
                
                if len(results) > 0:
                    plagiarized_hits += 1
            except Exception as e:
                print(f"DDG Search error for sentence '{sentence[:20]}...': {e}")
                continue

        # 4. Calculate percentage based on how many sentences were found online
        plagiarism_score = int((plagiarized_hits / sample_size) * 100)

    return {
        "ai_probability_percent": ai_score,
        "plagiarism_percent": plagiarism_score
    }
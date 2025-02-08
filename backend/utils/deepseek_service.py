from openai import OpenAI
import json
from .config import API_URL, API_KEY, SITE_URL, SITE_NAME

class DeepSeekService:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=API_KEY,
        )
        self.extra_headers = {
            "HTTP-Referer": SITE_URL,
            "X-Title": SITE_NAME,
        }
        
    def generate_dispute_summary(self, conversation):
        """Generates AI summary for admin review."""
        prompt = f"""
        Analyze this dispute conversation between a buyer and seller.
        Provide a concise summary for admin review:
        
        {conversation}
        
        Output format:
        - Summary:
        """
        
        return self._make_api_call(prompt)
    
    def detect_fraud_signals(self, conversation):
        """Analyzes text for potential fraud indicators."""
        prompt = f"""
        Analyze this conversation for potential fraud signals:
        
        {conversation}
        
        Output format:
        - Suspicious Patterns:
        - Risk Level (Low/Medium/High):
        - Highlighted Words: [List of suspicious words/phrases]
        """
        
        return self._make_api_call(prompt)
    
    def find_similar_cases(self, current_summary, past_cases):
        """Finds similar past cases."""
        prompt = f"""
        Compare this dispute summary with past cases:
        
        Current Case:
        {current_summary}
        
        Past Cases:
        {json.dumps(past_cases, indent=2)}
        
        Output format:
        - Most Similar Cases (Top 3):
        - Similarity Reasoning:
        - Relevant Precedents:
        """
        
        return self._make_api_call(prompt)
    
    def _make_api_call(self, prompt):
        """Makes the actual API call using OpenRouter."""
        try:
            completion = self.client.chat.completions.create(
                extra_headers=self.extra_headers,
                model="deepseek/deepseek-r1:free",
                messages=[
                    {"role": "system", "content": "You are an AI dispute resolution assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            return {"error": str(e)}


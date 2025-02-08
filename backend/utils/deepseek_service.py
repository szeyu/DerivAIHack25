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
        """Analyzes text for potential fraud indicators for both users."""
        try:
            prompt = f"""
            Analyze this conversation for potential fraud signals from both buyer and seller.
            Keep track of who says what and analyze each separately.

            Conversation:
            {conversation}

            Output format (strictly follow this format):
            BUYER ANALYSIS
            Highlighted Words: word1, word2, word3
            Suspicious Patterns: brief explanation
            Risk Level: Low/Medium/High

            SELLER ANALYSIS
            Highlighted Words: word1, word2, word3
            Suspicious Patterns: brief explanation
            Risk Level: Low/Medium/High
            """
            
            analysis = self._make_api_call(prompt)
            
            return {
                "userA": {
                    "name": "Buyer",
                    "analysis": analysis.split("SELLER ANALYSIS")[0].replace("BUYER ANALYSIS", "").strip()
                },
                "userB": {
                    "name": "Seller",
                    "analysis": analysis.split("SELLER ANALYSIS")[1].strip()
                }
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def find_similar_cases(self, current_summary, past_cases):
        """Finds similar past cases."""
        prompt = f"""
        Compare this dispute summary with past cases and output in simple format:
        
        Current Case:
        {current_summary}
        
        Past Cases:
        {json.dumps(past_cases, indent=2)}
        
        Output format (strictly follow):
        Most Similar Case: [single most relevant case]
        Reasoning: [one sentence explanation]
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


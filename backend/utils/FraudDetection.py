from semantic_router import Route
from semantic_router.layer import RouteLayer
from semantic_router.encoders import OpenAIEncoder  # You can also use CohereEncoder
import os
from dotenv import load_dotenv

# Set up OpenAI API Key (Replace with your actual API key)
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

class FraudDetection:
    def __init__(self):
        # Define suspicious phrases related to fraud
        fraud_route = Route(
            name="fraud",
            utterances=[
                "Let's continue on WhatsApp",
                "We can talk on Telegram",
                "Let's move to Messenger",
                "Switch to Signal",
                "Continue on WeChat",
                "Talk on Viber",
            ],
        )

        # Initialize encoder
        self.encoder = OpenAIEncoder()
        
        # Create RouteLayer with fraud detection route
        self.route_layer = RouteLayer(encoder=self.encoder, routes=[fraud_route])

    def is_suspicious(self, text: str) -> bool:
        """Check if the input text contains suspicious phrases."""
        return self.route_layer(text) is not None

    def detect_fraud(self, text: str):
        """Return the detected fraud category or None if no fraud detected."""
        result = self.route_layer(text)
        return result.name if result else None


# Example Usage
if __name__ == "__main__":
    fraud_detector = FraudDetection()
    
    test_phrases = [
        "Let's continue on WhatsApp",
        "We can talk on Telegram",
        "This is a normal message",
    ]
    
    for phrase in test_phrases:
        print(f"Input: {phrase} -> Suspicious: {fraud_detector.is_suspicious(phrase)}")

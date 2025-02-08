from semantic_router import Route
from semantic_router.layer import RouteLayer
from semantic_router.encoders import OpenAIEncoder  # Or use CohereEncoder if preferred
import os
from dotenv import load_dotenv
from typing import Tuple

# Set up OpenAI API Key (Replace with your actual API key)
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

class FraudDetection:
    def __init__(self):
        
        # --- Define sensitive keyword routes ---
        # Each sensitive category is defined as a separate route
        sensitive_routes = [
            Route(
                name="off_platform",
                utterances=[
                    "contact me on", "reach out to me at", "my number is", "message me on",
                    "find me on", "add me on", "i don't use this chat", "this chat is not secure",
                    "easier to talk on", "better communication on", "i prefer to use",
                    "let's continue on whatsapp", "we can talk on telegram", "talk on other platform"
                ],
            ),
            Route(
                name="urgency",
                utterances=[
                    "act fast!", "limited time offer!", "deal expires soon!", "urgent payment needed!",
                    "last chance!", "don't miss out!", "hurry, before it's gone!", "i need the money asap",
                    "send immediately"
                ],
            ),
            Route(
                name="info_request",
                utterances=[
                    "send me your login details", "what's your password?", "click this link to verify",
                    "scan this qr code", "give me your seed phrase", "share your recovery key", "install this app",
                    "run this program", "i need your secret code", "verify using this code"
                ],
            ),
            Route(
                name="bypass_security",
                utterances=[
                    "ignore the warnings", "skip the verification", "it's a safe link, trust me",
                    "don't worry about the security", "i'll take responsibility", "this is a shortcut",
                    "use this alternative method", "they won't notice", "this is a loophole", "there's a trick to it"
                ],
            ),
        ]
        self.sensitive_route_layer = RouteLayer(
            encoder=OpenAIEncoder(
                score_threshold=0.7
            ), 
            routes=sensitive_routes
        )


    def process_user_input(self, user_input: str, warning_count: int, llm) -> Tuple[str, int, bool]:
        """
        Process the user input by first checking for any sensitive content via the sensitive route layer.
        If a match is found, issue a warning (and escalate if necessary). Otherwise, format the fraud detection
        prompt with the input and pass it to the provided LLM.
        """
        escalate = False
        # Use the sensitive route layer from Semantic Router
        sensitive_result = self.sensitive_route_layer(user_input)
        if sensitive_result is not None and sensitive_result.name:
            warning_count += 1
            response = (
                "Warning: Your input contains potentially sensitive or inappropriate content. "
                "Please refrain from using language that violates platform policies. "
                "Continued use of such language may result in blocked access."
            )
            if warning_count >= 2:
                response += " ACTION REQUIRED: This user has exceeded the warning limit. Block further input and alert a human administrator."
                escalate = True
        else:
            response = "No sensitive content detected."
        return response, warning_count, escalate

# === Example Usage ===
if __name__ == "__main__":
    # Instantiate the fraud detection system using the Semantic Router Library
    fraud_detector = FraudDetection()
    
    # A sample LLM function (replace with your actual LLM call)
    llm = lambda prompt: f"LLM Response based on prompt:\n{prompt}"
    
    warning_count = 0

    while True:
        user_input = input("Enter your input: ")
        response, warning_count, escalate = fraud_detector.process_user_input(user_input, warning_count, llm)
        print(response)
        
        if escalate:
            print("Escalating to human administrator.")
            break  # or implement your escalation/blocking mechanism
        
        if warning_count >= 3:
            print("User has reached maximum warnings. Blocking further input.")
            break  # or implement your blocking mechanism

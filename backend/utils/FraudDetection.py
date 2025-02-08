from semantic_router import Route
from semantic_router.layer import RouteLayer
from semantic_router.encoders import OpenAIEncoder
import os
from dotenv import load_dotenv
from typing import Tuple

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SCORE_THRESHOLD = 0.7
MAX_WARNINGS = 1

# Validate environment variables
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")


class FraudDetector:
    def __init__(self):
        """Initialize fraud detection routes and semantic router layer"""
        self.route_layer = self._initialize_route_layer()

    def _initialize_route_layer(self) -> RouteLayer:
        """Configure the semantic routing layer with fraud detection rules"""
        routes = [
            Route(
                name="off_platform",
                utterances=[
                    "contact me on", "reach out to me at", "my number is",
                    "message me on", "find me on", "add me on",
                    "i don't use this chat", "this chat is not secure",
                    "easier to talk on", "better communication on",
                ],
            ),
            Route(
                name="urgency",
                utterances=[
                    "act fast!", "limited time offer!", "deal expires soon!",
                    "urgent payment needed!", "last chance!", "don't miss out!",
                ],
            ),
            Route(
                name="info_request",
                utterances=[
                    "send me your login details", "what's your password?",
                    "click this link to verify", "scan this qr code",
                    "give me your seed phrase", "share your recovery key",
                ],
            ),
            Route(
                name="bypass_security",
                utterances=[
                    "ignore the warnings", "skip the verification",
                    "it's a safe link, trust me", "don't worry about the security",
                    "i'll take responsibility", "this is a shortcut",
                ],
            ),
        ]

        return RouteLayer(
            encoder=OpenAIEncoder(score_threshold=SCORE_THRESHOLD),
            routes=routes
        )

    def analyze_text(self, text: str, warning_count: int) -> Tuple[str, int, bool]:
        """
        Analyze text for potential fraud indicators
        Returns:
            Tuple: (response message, new warning count, escalation flag)
        """
        route_choice = self.route_layer(text)
        escalate = False

        if route_choice and route_choice.name:
            warning_count += 1
            message = (
                "Warning: Your input contains potentially sensitive content. "
                "Repeated violations may lead to access restrictions."
            )
            
            if warning_count >= MAX_WARNINGS:
                message += " ACTION REQUIRED: Account suspension pending administrator review."
                escalate = True
        else:
            message = "No suspicious content detected."

        return message, warning_count, escalate
import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter configuration
API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = os.getenv('OPENROUTER_API_KEY', '')
SITE_URL = os.getenv('SITE_URL', 'http://localhost:5173')  # Your frontend URL
SITE_NAME = os.getenv('SITE_NAME', 'DerivAI Dispute Resolution')

# For testing/development
IS_TESTING = os.getenv('TESTING', 'False').lower() == 'true'
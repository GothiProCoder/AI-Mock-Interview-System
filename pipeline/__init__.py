# pipeline/__init__.py
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file variables into environment

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please add this to your .env file.")

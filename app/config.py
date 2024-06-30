import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
USE_EXAMPLES = os.getenv("USE_EXAMPLES", "False").lower() == "true"
LANGUAGE_MODELS = os.getenv("LANGUAGE_MODEL", "meta-llama/llama-3-70b-instruct:nitro").split(",")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

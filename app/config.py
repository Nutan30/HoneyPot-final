import os
import warnings
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

API_KEY = os.getenv("API_KEY", "CHANGE_THIS_SECRET_KEY")

# OpenAI LLM Configuration (Phase 2)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Database & Integration Settings
DATABASE_URL = os.getenv("DATABASE_URL", "")
GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL", "https://hackathon.guvi.in/api/updateHoneyPotFinalResult")

# Warn if running with default API key in non-test environments
if API_KEY == "CHANGE_THIS_SECRET_KEY" and "PYTEST_CURRENT_TEST" not in os.environ:
    warnings.warn(
        "\n⚠️  SECURITY WARNING: Running with default API key!\n"
        "   Set the API_KEY environment variable before deploying.\n"
        "   Example: export API_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')\n",
        UserWarning,
        stacklevel=2
    )

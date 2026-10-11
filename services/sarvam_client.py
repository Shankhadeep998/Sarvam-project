import os
from dotenv import load_dotenv
from sarvamai import SarvamAI

load_dotenv()

def get_sarvam_client() -> SarvamAI:
    """
    Initializes and returns the SarvamAI client using the API key
    configured in the environment.
    """
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise ValueError(
            "SARVAM_API_KEY is not set in the environment or .env file. "
            "Please configure your API key."
        )
    return SarvamAI(api_subscription_key=api_key)

import os
from dotenv import load_dotenv
from sarvamai import SarvamAI

# Load environment variables from .env
load_dotenv()

# Initialize the Sarvam AI client (reads SARVAM_API_KEY from environment)
client = SarvamAI(api_subscription_key=os.environ.get("SARVAM_API_KEY"))

response = client.chat.completions(
    model="sarvam-105b-conversations",
    messages=[
        {"role": "user", "content": "Hello! Introduce yourself in one short sentence."}
    ],
)

print(response.choices[0].message.content)

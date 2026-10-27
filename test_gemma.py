import os
from google import genai

if not os.getenv("GEMINI_API_KEY"):
    print("ERROR: API key environment variable missing.")
    raise SystemExit(1)

try:
    client = genai.Client()

    print("Connecting to Gemma 4...")

    response = client.models.generate_content(
        model="gemma-4-26b-a4b-it",
        contents=(
            "You are DisasterShield AI. "
            "Explain 3 important safety precautions during a flood. "
            "Use simple English."
        ),
    )

    print("\n--- DISASTERSHIELD | GEMMA 4 ---\n")
    print(response.text)

except Exception as error:
    print("Gemma 4 connection failed.")
    print("Error:", str(error))
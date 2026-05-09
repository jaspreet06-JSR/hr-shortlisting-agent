import os
import json

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def extract_candidate_data(text):

    prompt = f"""
    Extract the following information from this resume.

    Return ONLY valid JSON.

    Required fields:
    - skills
    - education
    - experience
    - projects

    Resume:
    {text}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    content = response.text

    # Clean markdown formatting
    content = content.replace("```json", "")
    content = content.replace("```", "")

    return json.loads(content)
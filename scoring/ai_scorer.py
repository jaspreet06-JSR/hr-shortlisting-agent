import os
import json

from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def evaluate_candidate(jd_text, candidate_data):

    prompt = f"""
    You are an expert HR evaluator.

    Evaluate the candidate based on the job description.

    Score each category from 0 to 10.

    Categories:
    - skills_match
    - experience_relevance
    - education
    - projects
    - communication

    Also provide:
    - short reason for each score
    - final overall score
    - recommendation

    Recommendation Rules:
    - 8+ = Strong Match
    - 6-7.9 = Moderate Match
    - below 6 = Weak Match

    Return ONLY valid JSON.

    JOB DESCRIPTION:
    {jd_text}

    CANDIDATE PROFILE:
    {candidate_data}
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
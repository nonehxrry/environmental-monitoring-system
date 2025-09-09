import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_alert(aqi_level: int, location: str = "your area"):
    """Generates a contextual alert based on high AQI."""
    prompt = f"""
    Generate a health and safety alert for an air quality index (AQI) of {aqi_level}. 
    The alert should be for {location} and include:
    1. A clear warning about health risks.
    2. Specific, actionable safety measures (e.g., wearing a mask, staying indoors).
    3. Be written in a helpful and clear tone, suitable for a mobile app notification.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an environmental monitoring assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error generating alert: {e}"

def chat_with_ai(query: str, current_aqi: int, location: str):
    """Handles general user queries about air quality."""
    prompt = f"""
    Current Air Quality Index (AQI) in {location} is {current_aqi}.
    The user is asking: "{query}"
    Provide a concise, helpful, and context-aware response.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and practical environmental expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error responding to query: {e}"
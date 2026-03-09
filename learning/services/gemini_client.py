import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash')

from google.api_core.exceptions import GoogleAPIError

def generate_response(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except GoogleAPIError as e:
        print(f"Gemini API Error: {e}")
        return None
    except Exception as e:
        print(f"Unknown Error during generation: {e}")
        return None
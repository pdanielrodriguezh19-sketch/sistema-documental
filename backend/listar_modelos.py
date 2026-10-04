import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.ai_api_key)

for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(model.name)
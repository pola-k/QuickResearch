import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import dotenv

dotenv.load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
IMAGE_MODEL = genai.GenerativeModel(model_name="gemini-2.5-flash")
CHAT_MODEL = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.0, google_api_key=GOOGLE_API_KEY)
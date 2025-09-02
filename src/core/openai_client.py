from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load OpenAI key from .env
load_dotenv()

def get_openai_llm():
    # You can add more config/env handling here
    return ChatOpenAI(
        temperature=0,
        model="gpt-4o-mini",
    )
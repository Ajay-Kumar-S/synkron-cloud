from langchain_ollama import OllamaLLM
from config import MODEL_NAME, BASE_URL

llm = OllamaLLM(
    model=MODEL_NAME,
    base_url=BASE_URL
)

def generate_response(prompt: str):
    return llm.invoke(prompt)

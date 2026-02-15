from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
from config import MEMORY_DIR, MODEL_NAME

embedding = OllamaEmbeddings(model=MODEL_NAME)

vectorstore = Chroma(
    persist_directory=MEMORY_DIR,
    embedding_function=embedding
)

def store_memory(text: str):
    doc = Document(page_content=text)
    vectorstore.add_documents([doc])
    vectorstore.persist()

def recall_memory(query: str, k: int = 3):
    results = vectorstore.similarity_search(query, k=k)
    return "\n".join([doc.page_content for doc in results])

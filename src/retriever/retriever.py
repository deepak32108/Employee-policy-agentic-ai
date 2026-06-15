from langchain_chroma import Chroma
from src.embeddings.embedding_model import get_embeddings

VECTOR_DB_PATH = "vectorstore"

_embeddings = get_embeddings()

_vector_db = Chroma(
    persist_directory=VECTOR_DB_PATH,
    embedding_function=_embeddings
)

_retriever = _vector_db.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 2}
)


def get_retriever():
    return _retriever


def retrieve_documents(question: str):
    docs = _retriever.invoke(question)
    return docs
from langchain_chroma import Chroma

from src.embeddings.embedding_model import get_embeddings

VECTOR_DB_PATH = "vectorstore"


def get_retriever():

    embeddings = get_embeddings()

    vector_db = Chroma(
        persist_directory=VECTOR_DB_PATH,
        embedding_function=embeddings
    )

    retriever = vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 2}
    )

    return retriever


def retrieve_documents(question: str):

    retriever = get_retriever()

    docs = retriever.invoke(question)

    return docs


if __name__ == "__main__":

    query = input("Ask Question: ")

    docs = retrieve_documents(query)

    print("\nRetrieved Documents:\n")

    for i, doc in enumerate(docs, start=1):

        print(f"\n----- Document {i} -----")
        print("Source:", doc.metadata.get("source"))
        print("Page:", doc.metadata.get("page"))
        print(doc.page_content[:500])
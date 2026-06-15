import os

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

from src.embeddings.embedding_model import get_embeddings


DATA_FOLDER = "data"
VECTOR_DB_PATH = "vectorstore"


def load_documents():

    documents = []

    pdf_files = [
        "leave_policy.pdf",
        "salary_policy.pdf",
        "working_policy.pdf"
    ]

    for pdf in pdf_files:

        pdf_path = os.path.join(DATA_FOLDER, pdf)

        print(f"Loading: {pdf}")

        loader = PyPDFLoader(pdf_path)

        docs = loader.load()

        # add source information
        for doc in docs:
            doc.metadata["source"] = pdf

        documents.extend(docs)

    return documents


def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    print(f"Total Chunks Created: {len(chunks)}")

    return chunks


def create_vector_database(chunks):

    embeddings = get_embeddings()

    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_PATH
    )

    print("\nVector Database Created Successfully")

    return vector_db


def main():

    print("\nLoading PDFs...\n")

    documents = load_documents()

    print(f"\nTotal Pages Loaded: {len(documents)}")

    print("\nCreating Chunks...\n")

    chunks = split_documents(documents)

    print("\nGenerating Embeddings...\n")

    create_vector_database(chunks)

    print("\nDone!")
    print(f"Database saved in: {VECTOR_DB_PATH}")


if __name__ == "__main__":
    main()
from src.retriever.retriever import retrieve_documents

question = "What is the leave policy?"

docs = retrieve_documents(question)

print(f"Found {len(docs)} documents\n")

for doc in docs:
    print(doc.page_content)
    print("-" * 50)

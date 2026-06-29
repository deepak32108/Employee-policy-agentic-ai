from src.retriever.retriever import _load_policy_documents


def main():
    documents = _load_policy_documents()

    print(
        f"Loaded {len(documents)} policy chunks from PDF files."
    )

    sources = sorted(
        {
            document.metadata["source"]
            for document in documents
        }
    )

    print(
        "Sources:"
    )

    for source in sources:
        print(
            f"- {source}"
        )


if __name__ == "__main__":
    main()
